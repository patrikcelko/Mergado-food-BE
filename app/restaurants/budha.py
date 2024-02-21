from __future__ import annotations

from .base_restaurant import BaseRestaurant


class BudhaRestaurant(BaseRestaurant):

    _ADDRESS = 'Náměstí Svobody 21'
    _URL = 'http://www.indian-restaurant-buddha.cz/'
    _NAME = 'Bhuddha Restaurant'
    _ACCEPTS_CARD = True

    def scrape(self) -> None:
        pass  # TODO implement
