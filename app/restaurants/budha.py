from __future__ import annotations
import logging
import re

from selenium.webdriver.common.by import By

from utility import WeekDays
from .base_restaurant import BaseRestaurant
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from selenium.webdriver.remote.webelement import WebElement
    from typing import List, Dict


class BudhaRestaurant(BaseRestaurant):

    _ADDRESS = 'Náměstí Svobody 21'
    _URL = 'http://www.indian-restaurant-buddha.cz/'
    _NAME = 'Bhuddha Restaurant'
    _ACCEPTS_CARD = True

    # Mapping of known alergens for restaurnat
    _ALERGENS_MAPPING: Dict[int, str] = {
        1: 'Lepek', 3: 'Vejce', 7: 'Mléčne výrobky', 8: 'Kešu a Kokos', 12: 'Glutaman',
    }

    def _map_alergens(self, raw_data: str) -> list:
        """Map alergens."""

        result: list = []
        for c in raw_data:
            if c.isdigit() and int(c) in self._ALERGENS_MAPPING:
                result.append(self._ALERGENS_MAPPING[int(c)])

        return result

    def _process_menu_item(self, raw_data: str, day: str) -> bool:
        """Process single item."""

        striped_raw_data: str = raw_data.replace(' ', '')
        is_soup: bool = False

        # Ignore lines with alergens and drinks
        if striped_raw_data.startswith('ALERGENY') or striped_raw_data.startswith('Nápoj'):
            return True

        # Remove soup starting word
        if striped_raw_data.startswith('Polévka'):
            raw_data = re.sub(r'Polévka:\s*', '', raw_data)
            is_soup = True

        money_pattern: str = r'(\d+,- Kč)$'
        match: re.Match[str] = re.search(money_pattern, raw_data)
        if not match:
            logging.warning(f'Was not able to find price {raw_data}')
            return False

        raw_price: str = match.group(1).replace(' ', '').split(',')[0]
        if not raw_price.isnumeric():
            logging.warning(f'Price is not numeric {raw_price}')
            return False

        # Remove price
        raw_data = re.sub(money_pattern, '', raw_data)
        alergens_pattern: str = r', A: [^)]+\)'
        alergens: List[str] = []

        alergens_match: re.Match[str] = re.search(alergens_pattern, raw_data)
        if alergens_match:
            alergens = self._map_alergens(alergens_match.group(0))

        # Remove alergens
        raw_data = re.sub(alergens_pattern, '', raw_data)

        parts: List[str] = raw_data.split('(')
        if len(parts) < 2:
            return False

        self.add_meal(day, parts[0].lstrip('* '), float(raw_price), parts[1], alergens, is_soup=is_soup)
        return True

    def scrape(self) -> bool:
        root_element: WebElement = self.web_driver.find_element(by=By.XPATH, value='/html/body/div/div[1]/div[3]/div')
        menus_elements: List[WebElement] = root_element.find_elements(by=By.CLASS_NAME, value='textmenu')

        days: List[str] = WeekDays.all_days()
        day_position: int = -1
        for menu_element in menus_elements:
            if len(menu_element.text) <= 1:
                continue  # Empty paragraph

            day_position += 1
            if day_position >= len(days):
                logging.debug(f'Early break in scraper for restaurant {self.name}.')
                break  # We reached end (Yes this could man that we do not load all neccessary data)

            for menu_item in menu_element.text.splitlines():
                if not self._process_menu_item(menu_item, days[day_position]):
                    return False

        return True
