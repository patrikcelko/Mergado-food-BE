from __future__ import annotations

from .base_restaurant import BaseRestaurant


class ThalieRestaurant(BaseRestaurant):

    _ADDRESS = 'Rooseveltova 14'
    _URL = 'https://www.thalie.cz/'
    _NAME = 'Thalie Restaurant'
    _ACCEPTS_CARD = True

    def scrape(self) -> None:
        pass  # TODO implement
