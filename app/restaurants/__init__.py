"""
Restaurants
===========

Package representing restaurants as a whole.
"""

from __future__ import annotations
import datetime
import logging
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


class RestaurantsManager:
    """Simple restaurant manager."""

    @staticmethod
    def execute_scraping(force_scraping: bool) -> int:
        """Start scraping on all avalible scrapers/restaurants."""

        failed_scrapings: int = 0

        for restaurant in RESTAURANTS:
            fail_already_detected: bool = False

            try:
                restaurant_instance: BaseRestaurant = restaurant()
                time_diff: datetime.datetime = datetime.now() - restaurant_instance.last_scraping

                if force_scraping or time_diff.second > SCRAPING_INTERVAL:
                    fail_already_detected = not restaurant_instance.scrape()
                    failed_scrapings += int(fail_already_detected)
                    restaurant_instance.save_meals()  # Save scraped data
            except Exception as exc:
                if not fail_already_detected:
                    failed_scrapings += 1

                logging.error(f'Scraping for restaurant {restaurant_instance.name} failed with exception: {str(exc)}.')
                logging.debug(f'Exception trace for restaurant {restaurant_instance.name}: {traceback.format_exc()}.')

    @staticmethod
    def get_restaurant_data(day: Optional[str], restaurant: Optional[str]) -> list:
        """Retrieve all restaurant data based on day and restaurant (hash ID of the restaurant) filter."""

        pass  # TODO implement fetching restaurant data


__all__ = ('BaseRestaurant', 'RestaurantsManager')
