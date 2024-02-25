"""
Config
======

Module containing all neccessary configs.
"""


# API config
DEBUG_MODE: bool = True  # Change this to `False` in production
VERSION: str = '1.0'

# Flask config
PORT: int = 5000
IP: str = '0.0.0.0'

# Redis config
REDID_IP: str = 'localhost'
REDIS_PORT: int = 6379
REDIS_SERVICE: str = 'redis'
