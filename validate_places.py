import json


def read_input_file(p):
    with open(p, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data



final_format_data = {}

for place in data['places']:
    for key, value in place.items():
        final_format_data[key] = value

for name, values in final_format_data.items():
    if 'types' not in values or 'restaurant' not in values['types']:
        print(name)

print(final_format_data.keys())

final_format_data['El+Del+Medio']


if __name__ == 'main.py':
    input_file = './restaurants.json'

    data = read_input_file(input_file)
    print(f"Number of places: {len(data['places'])}")