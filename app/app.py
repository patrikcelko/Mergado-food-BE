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
from restaurants import RESTAURANTS, RestaurantsFactory, BaseRestaurant
from config import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional


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
        data: list = RestaurantsFactory.get_restaurants_data(day, restaurant)

        return {
            'loaded_scrapers': len(RESTAURANTS),
            'data_size': len(data),
            'data': data,
        }


@api.resource('/force-scraping')
class ScraperResource(Resource):

    # NOTE: This only works in debug mode
    @marshal_with({'failed_scrapers': fields.Integer})
    def get(self):
        if not DEBUG_MODE:
            abort(404)

        failed: int = RestaurantsFactory.execute_scraping(force_scraping=True)
        logging.warning(f'{failed} scrapers failed during forced scraping.')

        return {
            'failed_scrapers': failed
        }


if DEBUG_MODE:
    logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    app.run(debug=DEBUG_MODE, host=IP, port=PORT)
