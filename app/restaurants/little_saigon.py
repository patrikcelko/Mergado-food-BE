from __future__ import annotations

from .base_restaurant import BaseRestaurant


class LittleSaigonRestaurant(BaseRestaurant):

    _ADDRESS = 'Špitálka 124/37'
    _URL = 'https://littlesaigon.cz/'
    _NAME = 'Little Saigon'
    _ACCEPTS_CARD = True

    def scrape(self) -> None:
        pass  # TODO implement
