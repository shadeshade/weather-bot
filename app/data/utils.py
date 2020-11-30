from app.data import CITIES_DATA


def get_city_data(city):
    """return the cities_db dictionary"""
    content = CITIES_DATA[city]
    return content
