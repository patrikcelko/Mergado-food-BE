# Mergado-food-BE

Simple API is written in Python which would return a list of menus for restaurants near the Mergado Technologies. These menus are stored in Redis and are periodically updated (using celery tasks) from restaurants' web pages (these data are simply scraped). This approach will prevent long delays in loading and eventual pseudo attack on the owner of the websites that we are scraping by just refreshing the API endpoint.

## Starting application

For better compatibility whole backend is contained in a docker container (4 containers: `redis`, `worker`, `web`, `scheduler`) which can be simply run using the included shell script `start.sh` (it will rebuild and start container).

## Adding a new restaurant

Adding a new restaurant is straightforward... Only what we need to do is to create a new Python file in the `restaurants` module with the class which would inherit from `BaseRestaurant` and overrides the `scrape` method which defines how we should scrape data and attributes such as `_ADDRESS`, `_URL`, `_NAME`, `_ACCEPTS_CARD`. After that, we just simply register it in the main module (we would just add this class to the list of available restaurants...).

## API Endpoints

- `/`: Home endpoint, returns version and current amount of loaded scrapers.
- `/restaurants`: Can use optional parameters such as *day* which filter only selected day or *restaurant* which would filter only restaurant equal to used ID.
- `/force-scraping`: Manualy force scraping (this is only avalible when debug is set to *True*)
