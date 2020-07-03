import json
source = ''

with open('cities_bd.json', 'r', encoding='utf-8') as f:
    data1 = json.load(f)


print(data1)
