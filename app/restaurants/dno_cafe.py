from __future__ import annotations

from .base_restaurant import BaseRestaurant


class DnoCafeRestaurant(BaseRestaurant):

    _ADDRESS = 'Orlí, 522/19'
    _URL = 'http://www.dnobrno.cz/'
    _NAME = 'Dno Restaurant & Café'
    _ACCEPTS_CARD = False

    def scrape(self) -> bool:
        # TODO implement
        return True
