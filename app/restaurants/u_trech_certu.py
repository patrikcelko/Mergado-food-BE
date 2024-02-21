from __future__ import annotations

from .base_restaurant import BaseRestaurant


class UTrechCertuRestaurant(BaseRestaurant):

    _ADDRESS = 'Dvořákova 6/8'
    _URL = 'https://ucertu.cz/'
    _NAME = 'U Trech certu'
    _ACCEPTS_CARD = True

    def scrape(self) -> None:
        pass  # TODO implement
