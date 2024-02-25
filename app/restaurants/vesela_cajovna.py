from __future__ import annotations

from .base_restaurant import BaseRestaurant


class VeselaCajovnaRestaurant(BaseRestaurant):

    _ADDRESS = 'Kobližná 5'
    _URL = 'https://www.veselacajovna.cz/'
    _NAME = 'Restaurace Vesela Cajovna'
    _ACCEPTS_CARD = True

    def scrape(self) -> bool:
        # TODO implement
        return True
