from __future__ import annotations

from .base_restaurant import BaseRestaurant


class ChillTreeRestaurant(BaseRestaurant):

    _ADDRESS = 'Orlí 542/27'
    _URL = 'https://chillitreevn.com/'
    _NAME = 'Chilli Tree Restaurant'
    _ACCEPTS_CARD = True

    def scrape(self) -> None:
        pass  # TODO implement
