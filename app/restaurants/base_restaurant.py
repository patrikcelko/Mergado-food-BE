from __future__ import annotations

import json
import logging

from datetime import datetime
from flask_restful import fields
from redis import Redis
from abc import abstractmethod
from utility import WeekDays, create_brno_like_address
from config import REDIS_PORT, REDIS_SERVICE
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List, Optional, Dict, Union


_UNKNOWN_VALUE: str = 'Unknown Value'


class RestaurantMeal:

    MEAL_FIELDS: dict = {
        'name': fields.String, 'price': fields.Float, 'description': fields.String,
        'alergens': fields.List(fields.String), 'is_vegan': fields.Boolean,
        'is_gluten_free': fields.Boolean, 'is_soup': fields.Boolean,
    }

    # NOTE: Float is not the best type for curency butt here it should do the job
    def __init__(self, name: str, price: float, description: Optional[str], alergens: Optional[List[str]],
                 is_vegan: bool = False, is_gluten_free: bool = False, is_soup: bool = False) -> None:
        self.name: str = name
        self.price: float = price
        self.description: str = description
        self.alergens: List['str'] = alergens
        self.is_vegan: bool = is_vegan
        self.is_gluten_free: bool = is_gluten_free
        self.is_soup: bool = is_soup

    def to_dict(self) -> dict:
        """Returns meal as dictonary."""

        return {
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'alergens': self.alergens,
            'is_vegan': self.is_vegan,
            'is_gluten_free': self.is_gluten_free,
            'is_soup': self.is_soup,
        }

    @staticmethod
    def from_dict(raw_dict: dict) -> RestaurantMeal:
        """Deserialize meal from the dict."""

        return RestaurantMeal(raw_dict.get('name', 'ERROR'), raw_dict.get('price', 0.0), raw_dict.get('description', ''),
                              raw_dict.get('alergens', []), raw_dict.get('is_vegan', False),
                              raw_dict.get('is_gluten_free', False), raw_dict.get('is_soup', False))

    @staticmethod
    def serialize_meals(data: Dict[str, List[RestaurantMeal]]) -> str:
        """Serialize meal to dict."""

        data_copy: Dict[str, List[dict]] = {}

        for day, meals in data.items():
            if isinstance(day, tuple):
                day = day[0]
            data_copy[str(day)] = list(map(lambda meal: meal.to_dict(), meals))

        return json.dumps(data_copy)

    @staticmethod
    def deserialize_meals(raw_meals: str) -> Dict[str, List[RestaurantMeal]]:
        """Try to get meals from Redis based on `restaurant_id`."""

        return_data: Dict[str, List[dict]] = {}

        for day, meals in json.loads(raw_meals).items():
            if isinstance(day, tuple):
                day = day[0]
            meals = list(map(lambda meal_raw: RestaurantMeal.from_dict(meal_raw), meals))
            return_data[day] = meals

        return return_data


class BaseRestaurant:

    RESTAURANT_FIELDS: dict = {
        'name': fields.String, 'url': fields.String, 'accepts_cards': fields.Boolean, 'last_scrape': fields.String,
        'meals': fields.Nested(fields.Nested(RestaurantMeal.MEAL_FIELDS))
    }

    _ADDRESS: str = _UNKNOWN_VALUE
    _URL: str = _UNKNOWN_VALUE
    _NAME: str = _UNKNOWN_VALUE
    _ACCEPTS_CARD: bool = False

    # Creating empty meals
    MEALS: Dict[str, List[RestaurantMeal]] = dict(map(lambda day: (day, []), WeekDays.all_days()))

    def _init_scrapers(self) -> None:
        """Initialise selenium scraper."""

        if self.web_driver is not None:
            return  # It is already initialised.

        chrome_options: Options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'")

        # Selenium scraper
        self.web_driver = Chrome(options=chrome_options)
        self.web_driver.get(self._URL)
        self.web_driver.implicitly_wait(0.5)  # Load page

        logging.info(f'Startig scraping for page "{self.web_driver.title}".')


    def __init__(self, force_scrape: bool = False, ignore_loading: bool = False, init_scaper: bool = False) -> None:
        self._last_scraping: Optional[datetime] = None
        self.web_driver: Optional[Chrome] = None

        if init_scaper:
            self._init_scrapers()

        self.redis_client: Redis = Redis(host=REDIS_SERVICE, port=REDIS_PORT, decode_responses=False)
        # If the client does not response directly kill app by exception
        self.redis_client.ping()

        _reqired_data: List[str] = [self._ADDRESS, self._URL, self._NAME]
        if _UNKNOWN_VALUE in _reqired_data:
            # We found scraper that does not have filled required attributes.
            raise NotImplemented(f'Some attributess are not filled correctly: {_reqired_data}.')

        # If we are creating instance for scraping we do not need to load data which we will instantly
        # replace by  new one.
        if not ignore_loading:
            self.load_meals(force_scrape=force_scrape)  # Load meals from redis, or scrape them

    def __del__(self):
        if self.web_driver is not None:
            self.web_driver.close()

    @property
    def address(self) -> str:
        """Retrieve restaurant address."""

        if self._ADDRESS == _UNKNOWN_VALUE:
            raise ValueError('Getting address from uninitialised restaurant.')
        return create_brno_like_address(self._ADDRESS)

    @property
    def accept_cards(self) -> bool:
        """True if restaurant accepts cards."""

        return self._ACCEPTS_CARD

    @property
    def name(self) -> str:
        """Return restaurant name."""

        return self._NAME

    @property
    def _hash(self) -> int:
        """Unique identifier for the restaurant."""

        return hash(f'{self._URL}-{self.name}')

    @property
    def meals(self, day: Optional[str] = None) -> Union[List[RestaurantMeal], List[Dict[str, List[RestaurantMeal]]]]:
        """Retrieve meals for the specific day."""

        # Day is not specified, so we would take it as whole
        if not day:
            return self.MEALS

        if not WeekDays.is_valid_day(day) and day not in self.MEALS.keys():
            raise KeyError(f'Unknown day: {day}')
        retrieved_data: List[RestaurantMeal] = self.MEALS.get(day, [])
        if not retrieved_data:
            self.load_meals()  # Attempt to load if not already loaed
        return self.MEALS.get(day, [])

    @property
    def last_scraping(self) -> datetime:
        """Retrieve last datetime when was scraping executed."""

        redis_key: str = f'{self.name.replace(" ", "")}-{self._hash}-last_scraping'

        # Attempt to fetch
        if not self._last_scraping:
            self._last_scraping = self.redis_client.get(redis_key)

        if not self._last_scraping:
            return datetime.fromtimestamp(0)  # Scraping does not exists
        return self._last_scraping

    @abstractmethod
    def scrape(self) -> bool:
        """Callback method for scraping."""

        raise NotImplemented('Calling unimplemented scraper.')

    def to_dict(self, day: Optional[str] = None) -> dict:
        """Create dictonary like representation of the restaurant and their meals."""

        meals_data: dict = {}
        if day:
            _meals: list = list(map(lambda meal: meal.to_dict(), self.meals(day=str(day))))
            meals_data[str(day)] = _meals
        else:
            for _day, _meals in self.meals.items():
                if isinstance(_day, tuple):
                    _day = _day[0]  # Fix binding problem.
                meals_data[str(_day)] = list(map(lambda meal: meal.to_dict(), _meals))

        return {
            'name': self.name,
            'url': self._URL,
            'accepts_cards': self.accept_cards,
            'last_scrape': str(self.last_scraping),
            'meals': meals_data
        }

    def add_meal(self, day: str, name: str, price: float, description: Optional[str] = None,
                 alergens: Optional[List[str]] = None, is_vegan: bool = False,
                 is_gluten_free: bool = False, is_soup: bool = False) -> bool:

        self.MEALS[day].append(RestaurantMeal(name, price, description, alergens, is_vegan,
                                              is_gluten_free, is_soup))
        logging.debug(f'Successfully added meal for day {day} with data: {self.MEALS[day][-1]}.')
        return True

    def load_meals(self, force_scrape: bool = False) -> None:
        """Load meals from redis if possible."""

        redis_key: str = f'{self._hash}-meals'
        raw_meals: str = self.redis_client.get(redis_key)

        if force_scrape or not raw_meals:
            # During scraping we should already fill MEALS atribute
            logging.debug(f'Starting scraping for restaurant {self.name} in load request.')
            self._init_scrapers()  # Try to init scraper if is not already initialised
            self.scrape()
            return self.save_meals()

        logging.debug(f'Starting meals deserialization (loading) for restaurant {self.name}.')
        self.MEALS = RestaurantMeal.deserialize_meals(raw_meals)

    def save_meals(self) -> None:
        """Save meals to redis if possible."""

        redis_key: str = f'{self._hash}-meals'

        logging.debug(f'Starting meals serialization (saving) for restaurant {self.name}.')
        self.redis_client.set(redis_key, RestaurantMeal.serialize_meals(self.MEALS))
