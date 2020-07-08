import json

js1 = open('cities_data.json', encoding='utf-8')
js2 = open('cities_data2.json', encoding='utf-8')
js3 = open('cities_data3.json', encoding='utf-8')

data1 = json.load(js1)
data2 = json.load(js2)
data3 = json.load(js3)
cities = {}

for k, v in data1.items():
    cities[k] = v
for k, v in data2.items():
    cities[k] = v
for k, v in data3.items():
    cities[k] = v

with open('temp_cities_db.json', 'w', encoding='utf-8') as f:
    json.dump(cities, f, ensure_ascii=False, indent=4)

js1.close()
js2.close()
js3.close()