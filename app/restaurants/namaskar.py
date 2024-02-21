from __future__ import annotations

from .base_restaurant import BaseRestaurant


class NamaskarRestaurant(BaseRestaurant):

    _ADDRESS = 'Smetanova 3'
    _URL = 'https://www.namaskar.cz/'
    _NAME = 'Namaskar'
    _ACCEPTS_CARD = True

    def scrape(self) -> None:
        pass  # TODO implement
