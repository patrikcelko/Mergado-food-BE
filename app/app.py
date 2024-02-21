"""
Restaurant Menus scraper
========================

Main entry point for scraping API.
"""

from __future__ import annotations

import logging

from flask import Flask
from flask_cors import CORS
from flask_restful import Api, Resource, abort, marshal_with, fields

from utility import CoerceWith
from restaurants import RESTAURANTS, RestaurantsManager, BaseRestaurant

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional


# CONFIG
DEBUG_MODE: bool = True  # Change this to `False` in production
VERSION: str = '1.0'
PORT: int = 5000
IP: str = '0.0.0.0'

# FLASK
app: Flask = Flask(__name__)
api: Api = Api(app)
cors: CORS = CORS(app)


@api.resource('/')
class RootResource(Resource):

    @marshal_with({'version': fields.String, 'loaded_scrapers': fields.Integer})
    def get(self):
        return {
            'version': VERSION,
            'loaded_scrapers': len(RESTAURANTS)
        }


@api.resource('/restaurants')
class RestaurantResource(Resource):

    marshal_with(
        {
            'loaded_scrapers': fields.Integer,
            'data': fields.List(fields.Nested(BaseRestaurant.RESTAURANT_FIELDS))
        }
    )
    CoerceWith(CoerceWith.RESTAURANT_FIELDS)
    def get(self, day: Optional[str] = None, restaurant: Optional[str] = None):
        return {
            'loaded_scrapers': len(RESTAURANTS),
            'data': RestaurantsManager.get_restaurant_data(day, restaurant)
        }


@api.resource('/force-scraping')
class ScraperResource(Resource):

    # NOTE: This only works in debug mode
    @marshal_with({'failed_scrapers': fields.Integer})
    def get(self):
        if not DEBUG_MODE:
            abort(404)

        failed: int = RestaurantsManager.execute_scraping(force_scraping=True)
        logging.warning(f'{failed} scrapers failed during forced scraping.')

        return {
            'failed_scrapers': failed
        }


if __name__ == '__main__':
    app.run(debug=DEBUG_MODE, host=IP, port=PORT)
