"""
Utility
=======

Collection of miscellaneous functions used in this app.
"""

from __future__ import annotations

import os
import uuid
import pytesseract

from collections import defaultdict
from copy import deepcopy
from enum import Enum
from functools import wraps
from flask import Request, abort
from flask_restful import fields, reqparse
from flask import request as flask_request
from PIL import Image

from typing import TYPE_CHECKING, Iterable

import urllib3
if TYPE_CHECKING:
    from typing import List, Callable, Optional


BRNO_CITY_CODE_ADDRESS: str = 'Brno (602 00)'
TEMP_FILE_PATH: str = os.path.join(os.path.realpath(__file__), 'temp')


class WeekDays(Enum):

    MONDAY: str = 'Monday'
    TUESDAY: str = 'Tuesday',
    WEDNESDAY: str = 'Wednesday'
    THURSDAY: str = 'Thursday',
    FRIDAY: str = 'Friday',
    # NOTE: We would not count here Sunday or Saturday

    def __str__(self) -> str:
        return self.value

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, str) and __value == self.value

    @staticmethod
    def all_days() -> List[str]:
        return [data.value for data in WeekDays]

    @staticmethod
    def is_valid_day(day_str) -> bool:
        return day_str in WeekDays.all_days()

    def __hash__(self) -> int:
        return hash(self.value)


def create_brno_like_address(street_address: str) -> str:
    return f'{street_address}{BRNO_CITY_CODE_ADDRESS}'


def filter_dict(d, include: Optional[Iterable] = None, omit: Optional[Iterable] = None) -> dict:
    """Takes dict d and returns a similar one, which contains only keys mentioned
    in included iterable.
    """

    if include:
        filtered: dict = {}
        for key in include:
            if key in d:
                filtered[key] = d[key]
        return filtered

    if omit:
        filtered: dict = dict(d)
        for key in omit:
            if key in d:
                del filtered[key]

    return filtered


def filter_fields(d: dict, include_fields: Iterable[str]) -> dict:
    """Takes dict d and returns a similar one, which contains only keys mentioned in
    fields iterable. Those are supported not only as flat keys, but also as nested paths
    separated by dots. Such paths can reach also dicts nested in d.
    """

    if not include_fields:
        return d

    # Work with a shallow copy - do not modify the original dict argument.
    d: dict = dict(d)

    # Flat fields, e.g. url, process, limit
    flat: set = set([f for f in include_fields if '.' not in f])
    nested: set = set(include_fields) - flat

    # Support for filtering sub-fields, e.g. error.name, error.message
    mapping: dict = defaultdict(set)

    for field in nested:
        head, remain = field.split('.', 1)
        if head in d and head not in flat:
            mapping[head].add(remain)

    new_nested: dict = {}
    for field, sub in mapping.items():
        if d[field].nested is None:
            new_nested = dict.fromkeys(sub, fields.String())
            continue
        new_nested = filter_dict(d[field].nested, sub)

        # Copy original to overwrite only `nested` attribute and not others
        copied_field = deepcopy(d[field])
        copied_field.nested = new_nested
        d[field] = copied_field
        flat.add(field)

    return filter_dict(d, flat)


class EnumField(fields.String):
    """Enum field."""

    def __init__(self, values: List[str], name: Optional[str] = None, *args, **kwargs) -> None:
        self._values: List[str] = values
        self._name: Optional[str] = name
        super(EnumField, self).__init__(*args, **kwargs)

    def parse(self, value) -> str:
        value: str = str(value)
        if value not in self._values:
            raise fields.MarshallingException(f'Possible values: {", ".join(self._values)}')

        return value


class CoerceWith:
    """Method decorator to simplify validation of input data."""

    RESTAURANT_FIELDS: dict = {
        'day': EnumField(WeekDays.all_days() + ['all'], default='all'),
        'restaurant': fields.String
    }

    def __init__(self, coerce_fields: dict, location: str = 'json') -> None:
        self.fields: dict = coerce_fields
        self.location: str = location

    def __call__(self, view) -> Callable:
        @wraps(view)
        def wrapper(obj_self, *args, **kwargs):
            return view(
                obj_self,
                self._coerce_input(),
                *args, **kwargs
            )

        return wrapper

    def _coerce_input(self, request: Optional[Request] = None) -> dict:
        """Helper simplifying validation of input data.

        Function takes *fields_data* dict with fields_data and constructs RequestParser` according
        to those. Thus, input validation is fully automatic and very similar to output marshalling.
        Returns only items which are not `None`.
        """

        parser: reqparse.RequestParser = reqparse.RequestParser()
        request: Request = request or flask_request

        content_type: str = request.headers.get('Content-Type', '')
        if self.location == 'json' and 'application/json' not in content_type:
            abort(400, message="Bad Content-Type, JSON expected.")

        if request.method in ['PATCH', 'PUT']:
            # Allow partial update
            incoming_keys: list = list(getattr(request, self.location).keys())
            fields_data: dict = filter_fields(self.fields, incoming_keys)

        # Allow None values for selected fields
        nullables: set = set()
        for name, field in fields_data.items():
            if field.nullable:
                nullables.add(name)

            parser.add_argument(
                name, type=field.parse, default=field.default, required=field.required,
                location=self.location, dest=field.attribute or name,
                help=f'Field {name} is not in required format.'
            )

        data: dict = parser.parse_args(req=request)
        return {k: v for k, v in data.items() if v is not None or k in nullables}


def download_image(url: str) -> None:
    """Download image from URL and save it to temp file."""

    img_hash: str = uuid.uuid4().hex
    urllib3.urlretrieve(url, os.path.join(TEMP_FILE_PATH, f'{img_hash}.png'))


def image_to_text(image_name: str) -> str:
    """Retrieve text from image and returns it."""

    return pytesseract.image_to_string(Image.open(os.path.join(TEMP_FILE_PATH, image_name)))
