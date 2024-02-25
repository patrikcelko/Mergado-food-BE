"""
Tasks
=====

Module containing all available celery tasks Mainly the one used for scraping restaurant pages.
"""

from __future__ import annotations

import logging
import os
import time

from celery import Celery
from restaurants import RESTAURANTS, RestaurantsFactory
from config import REDIS_PORT, REDID_IP


CELERY_BROKER_URL: str = os.environ.get('CELERY_BROKER_URL', f'redis://{REDIS_PORT}:{REDIS_PORT}'),
CELERY_RESULT_BACKEND: str = os.environ.get('CELERY_RESULT_BACKEND', f'redis://{REDIS_PORT}:{REDIS_PORT}')
TASK_REPEAT_TIME: int = 3600  # 1 hour


def _init_celery(_broker: str, _backend: str) -> Celery:
    """Initialize all necessary Celery configs."""

    _celery: Celery = Celery('tasks', broker=_broker, backend=_backend)
    _celery.conf.timezone = 'UTC'

    return _celery


# Global Celery instance
celery: Celery = _init_celery(CELERY_BROKER_URL, CELERY_RESULT_BACKEND)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs) -> None:
    """Register periodic tasks."""

    sender.add_periodic_task(float(TASK_REPEAT_TIME), scrape, name='periodic_scraping')


@celery.task(name='tasks.scraping', soft_time_limit=1800)
def scrape(force_scraping: bool = False) -> None:
    """A task that would scrape and update all necessary data about restaurant menus.

    :param force_scraping: If `True` all menus will be scared no matter how old data are.

    NOTE: Task time limit is 30 minutes.
    """

    logging.info(f'Scraping task was executed. Updating data from {len(RESTAURANTS)} restaurants.')

    start_time: float = time.time()

    # Execute scraping on all restaurants
    failed: int = RestaurantsFactory.execute_scraping(force_scraping)

    logging.info(f'Scraping was done in {(time.time() - start_time):.2f}s, {failed} scrapers failed.')
