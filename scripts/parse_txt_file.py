import json

cities = {}
with open('weather.txt') as f:
    lines = f.readlines()

    for line in lines:
        line = line.replace(',', '')
        line = line.split()
        idx = line.index('->')

        ru_name = line[0]
        eng_name = line[idx + 1]
        cities[ru_name] = eng_name

with open('cities_data.json', 'w', encoding='utf-8') as f:
    json.dump(cities, f, ensure_ascii=False, indent=4)
