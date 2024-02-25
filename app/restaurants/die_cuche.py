from __future__ import annotations

from .base_restaurant import BaseRestaurant


class DieChucheRestaurant(BaseRestaurant):

    _ADDRESS = 'Kabinet MÚZ, Sukova 4'
    _URL = 'https://www.diekuche.cz/'
    _NAME = 'Restaurant Die Kuche'
    _ACCEPTS_CARD = False

    def scrape(self) -> bool:
        # TODO implement
        return True
