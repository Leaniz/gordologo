import pandas as pd
import requests
import json

def get_api_key(p):
    with open(p, 'r') as f:
        api_key = f.read()
    return api_key

def get_places_names(csv_p):
    """get places names from exported URL"""
    df = pd.read_csv(csv_p)
    return [p.split('/')[5] for p in df.URL.tolist()]

def get_places_info_from_names(places_names, api_key):
    """
        Call Google API to get places information.
    """
    places_json = {'places': [],
                    'ambiguous_places': [],
                    'places_not_found': []
                    }

    return_fields = ['place_id',
                    'formatted_address',
                    'name',
                    'rating',
                    'types',
                    'price_level',
                    'user_ratings_total']

    for i, place in enumerate(places_names):
        if not i % 10:
            print(f'{i} places processed')
        str_returns_fields = ','.join(return_fields)
        r = requests.get(f'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={place}&inputtype=textquery&fields={str_returns_fields}&key={api_key}')
        if r.status_code == 200:
            place_data = r.json()
            n_candidates = len(place_data['candidates']) 
            if n_candidates == 1:
                places_json['places'].append({place: place_data['candidates'][0]})
            elif n_candidates == 0:
                places_json['places_not_found'].append({place: place_data['candidates']})
            else:
                places_json['ambiguous_places'].append({place: place_data['candidates']})
        else:
            print(f'Unsuccesful request:\n {r.json()}')
            return places_json, False
    
    return places_json, True

def save_places(output_p, places_json):
    with open(output_p, 'w', encoding='utf-8') as f:
        json.dump(places_json, f, ensure_ascii=False)


if __name__ == '__main__':
    # "Quiero ir" file comes from Google Takeout, selecting "Save" category <https://takeout.google.com/settings/takeout?hl=es>
    input_file = './data/Quiero ir.csv'
    api_key_file = './api_key.txt'
    output_file = './data/restaurants.json'

    api_key = get_api_key(api_key_file)
    places_names = get_places_names(input_file)

    places_json, val = get_places_info_from_names(places_names, api_key)
    if val:
        save_places(output_file, places_json)
    else:
        print("Results not saved due to unsuccessful request")
