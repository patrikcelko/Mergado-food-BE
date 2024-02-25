"""
Restaurants
===========

Package representing restaurants as a whole.
"""

from __future__ import annotations
from datetime import datetime
import logging
import time
import traceback

from .base_restaurant import BaseRestaurant
from .budha import BudhaRestaurant
from .chilli_tree import ChillTreeRestaurant
from .die_cuche import DieChucheRestaurant
from .dno_cafe import DnoCafeRestaurant
from .little_saigon import LittleSaigonRestaurant
from .namaskar import NamaskarRestaurant
from .parodie import ParodieRestaurant
from .pivnice_na_rohu import PivniceNaRohuRestaurant
from .stara_tkalcovska import StaraTkalcovskaRestaurant
from .thalie import ThalieRestaurant
from .u_trech_certu import UTrechCertuRestaurant
from .vesela_cajovna import VeselaCajovnaRestaurant

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List, Type, Optional


# After how much time we can do scraping
SCRAPING_INTERVAL: int = 2700  # 45 minutes

# Listing of all avalible restaurant scrapers classes.
# NOTE: If you want to add restaurant just add corresponding class and you are DONE.
RESTAURANTS: List[Type] = [
    BudhaRestaurant, ChillTreeRestaurant, DieChucheRestaurant, DnoCafeRestaurant, LittleSaigonRestaurant,
    NamaskarRestaurant, ParodieRestaurant, PivniceNaRohuRestaurant, StaraTkalcovskaRestaurant,
    ThalieRestaurant, UTrechCertuRestaurant, VeselaCajovnaRestaurant,
]

class RestaurantsFactory:
    """Simple restaurant manager."""

    @staticmethod
    def execute_scraping(force_scraping: bool) -> int:
        """Start scraping on all avalible scrapers/restaurants."""

        failed_scrapings: int = 0
        accum_time: float = 0

        for restaurant in RESTAURANTS:
            start_time: float = time.time()
            fail_already_detected: bool = False
            errors_count: int = 0
            restaurant_name: str = None
            restaurant_instance: Optional[BaseRestaurant] = None

            try:
                restaurant_instance = restaurant()
                restaurant_name = restaurant_instance.name
                logging.info(f'Starting scraping for restauran {restaurant_instance.name}.')
                time_diff: datetime = datetime.now() - restaurant_instance.last_scraping

                if force_scraping or time_diff.second > SCRAPING_INTERVAL:
                    fail_already_detected = not restaurant_instance.scrape()
                    failed_scrapings += int(fail_already_detected)
                    restaurant_instance.save_meals()  # Save scraped data
            except Exception as exc:
                if not fail_already_detected:
                    failed_scrapings += 1

                if not restaurant_name:
                    logging.error(f'Was not able to instanciate {restaurant.__name__}.')
                    restaurant_name = f'CLASS-{restaurant.__name__}'

                logging.error(f'Scraping for restaurant {restaurant_name} failed with exception: {str(exc)}.')
                logging.debug(f'Exception trace for restaurant {restaurant_name}: {traceback.format_exc()}.')

            time_diff: float = time.time() - start_time
            accum_time += time_diff
            logging.info(f'Scraping for restaurant {restaurant_name} was done in {time_diff:.2f}.')
        logging.info(f'Scraping task was done in {accum_time} with {errors_count} errors.')

        return failed_scrapings


    @staticmethod
    def get_restaurants_data(day: Optional[str], restaurant_name: Optional[int]) -> list:
        """Retrieve all restaurants data based on day and restaurant (hash ID of the restaurant) filter."""

        _restaurant_name: str = None
        restaurant_instance: Optional[BaseRestaurant] = None
        resulting_restaurants: list = []

        for restaurant in RESTAURANTS:
            try:
                restaurant_instance = restaurant()
                _restaurant_name = restaurant_instance.name

                if restaurant_name and restaurant_name.replace(' ', '') not in restaurant_instance.name.replace(' ', ''):
                    continue  # Filtering by name

                resulting_restaurants.append(restaurant_instance.to_dict(day))

            except Exception as exc:
                if not _restaurant_name:
                    logging.error(f'Was not able to instanciate {restaurant.__name__}.')
                    _restaurant_name = f'CLASS-{restaurant.__name__}'

                logging.error(f'Loading restaurant {_restaurant_name} failed with exception: {str(exc)}.')
                logging.debug(f'Exception trace for restaurant {_restaurant_name}: {traceback.format_exc()}.')
                continue

        return resulting_restaurants


__all__ = ('BaseRestaurant', 'RestaurantsFactory')
