import json
import os

CUR_PATH = os.path.abspath(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(CUR_PATH))
DATA_DIR = os.path.join(BASE_DIR, 'data')

with open(os.path.join(DATA_DIR, 'temp_cities_db.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)
    cities = {}

    for k, v in data.items():
        if ' ' in v:
            v = v.replace(' ', '-')
        if '(' in v:
            v = v.replace('(', '')
        if ')' in v:
            v = v.replace(')', '')
        if '(' in k:
            k_temp = k.split('(')
            k_temp1 = k_temp[0].strip()
            k_temp2 = k_temp[-1].split(')')[0]
            cities[k_temp1] = v
            cities[k_temp2] = v
            continue
        cities[k] = v

with open(os.path.join(DATA_DIR, 'cities_db.json'), 'w', encoding='utf-8') as f1:
    json.dump(cities, f1, ensure_ascii=False, indent=4)
