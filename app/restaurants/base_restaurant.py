from __future__ import annotations

import datetime

from abc import abstractmethod
from utility import WeekDays, create_brno_like_address

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List, Optional, Dict


_UNKNOWN_VALUE: str = 'Unknown Value'


class BaseRestaurant:

    RESTAURANT_FIELDS: dict = {
        # TODO implement
    }

    _ADDRESS: str = _UNKNOWN_VALUE
    _URL: str = _UNKNOWN_VALUE
    _NAME: str = _UNKNOWN_VALUE
    _ACCEPTS_CARD: bool = False

    # Creating empty meals
    MEALS: Dict[str, List[RestaurantMeal]] = dict(map(lambda day: (day, []), WeekDays.all_days()))

    def __init__(self, force_scrape: bool = False, ignore_loading: bool = False) -> None:
        self._last_scraping: Optional[datetime.datetime] = None

        _reqired_data: List[str] = [self._ADDRESS, self._URL, self._NAME]
        if _UNKNOWN_VALUE in _reqired_data:
            # We found scraper that does not have filled required attributes.
            raise NotImplemented(f'Some attributess are not filled correctly: {_reqired_data}.')

        # If we are creating instance for scraping we do not need to load data which we will instantly
        # replace by  new one.
        if not ignore_loading:
            self.load_meals(force_scrape=force_scrape)  # Load meals from redis, or scrape them

    @property
    def address(self) -> str:
        """Retrieve restaurant address."""

        if self._ADDRESS == _UNKNOWN_VALUE:
            raise ValueError('Getting address from uninitialised restaurant.')
        return create_brno_like_address(self._ADDRESS)

    @property
    def accept_cards(self) -> bool:
        """True if restaurant accepts cards."""

        return self._ACCEPT_CARDS

    @property
    def name(self) -> str:
        """Return restaurant name."""

        self._NAME

    @property
    def _hash(self) -> int:
        """Unique identifier for the restaurant."""

        return hash(f'{self._URL}-{self._NAME}')

    @property
    def meals(self, day: str) -> List[RestaurantMeal]:
        """Retrieve meals for the specific day."""

        if not WeekDays.is_valid_day(day) and day not in self.MEALS.keys:
            raise KeyError(f'Unknown day: {day}')
        return self.MEALS.get(day, [])

    @property
    def last_scraping(self) -> datetime.datetime:
        """Retrieve last datetime when was scraping executed."""

        if not self._last_scraping:
            pass  # TODO implement
        return self._last_scraping

    @abstractmethod
    def scrape(self) -> None:
        """Callback method for scraping."""

        raise NotImplemented('Calling unimplemented scraper.')


    def load_meals(self, force_scrape: bool = False) -> None:
        """Load meals from redis if possible."""

        if force_scrape:
            # During scraping we should already fill MEALS atribute
            self.scrape()
            return self.save_meals()

        self.meals = RestaurantMeal.get_meals(self._hash)

    def save_meals(self) -> None:
        """Save meals to redis if possible."""

        pass  # TODO implement


class RestaurantMeal:

    MEAL_FIELDS: dict = {
        # TODO implement
    }

    # NOTE: Float is not the best type for curency butt here it should do the job
    def __init__(self, name: str, price: float, description: Optional[str], alergens: Optional[List[str]],
                 is_vegan: bool = False, is_gluten_free: bool = False) -> None:
        self.name = name
        self.price = price
        self.description = description
        self.alergens = alergens
        self.is_vegan = is_vegan
        is_gluten_free

    @staticmethod
    def get_meals(restaurant_id: int) -> List[RestaurantMeal]:
        """Try to get meals from Redis based on `restaurant_id`."""

        pass  # TODO implement
