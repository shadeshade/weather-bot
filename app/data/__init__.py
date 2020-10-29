import json
import os

CUR_PATH = os.path.realpath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(CUR_PATH))
DATA_DIR = os.path.join(BASE_DIR, 'data')


with open(os.path.join(DATA_DIR, 'cities_db.json'), 'r', encoding='utf-8') as f:
    CITIES_DATA = json.load(f)
