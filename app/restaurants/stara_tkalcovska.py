from __future__ import annotations

from .base_restaurant import BaseRestaurant


class StaraTkalcovskaRestaurant(BaseRestaurant):

    _ADDRESS = 'Bratislavská 52'
    _URL = 'https://www.efihotel.cz/stara-tkalcovna-poledni-menu/'
    _NAME = 'Restaurant Stara Tkalcovna'
    _ACCEPTS_CARD = False

    def scrape(self) -> bool:
        # TODO implement
        return True
