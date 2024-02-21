from __future__ import annotations

from .base_restaurant import BaseRestaurant


class ParodieRestaurant(BaseRestaurant):

    _ADDRESS = 'Vachova 8'
    _URL = 'https://parodierestaurant.cz/'
    _NAME = 'Parodie Restaurant'
    _ACCEPTS_CARD = True

    def scrape(self) -> None:
        pass  # TODO implement
