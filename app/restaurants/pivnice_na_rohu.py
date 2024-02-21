from __future__ import annotations

from .base_restaurant import BaseRestaurant


class PivniceNaRohuRestaurant(BaseRestaurant):

    _ADDRESS = 'Divadelní 6'
    _URL = 'https://www.pivnicenarohu.cz/'
    _NAME = 'Pivnice na Rohu'
    _ACCEPTS_CARD = True

    def scrape(self) -> None:
        pass  # TODO implement
