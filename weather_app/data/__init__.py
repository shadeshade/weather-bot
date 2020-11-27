import json
import os

DATA_DIR = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(DATA_DIR, 'cities_db.json'), 'r', encoding='utf-8') as f:
    CITIES_DATA = json.load(f)
