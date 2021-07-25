import pandas as pd
import googlemaps
import json
from elasticsearch import Elasticsearch

def get_api_key(p):
    with open(p, 'r') as f:
        api_key = f.read()
    return api_key

def get_places_names(csv_p):
    """get places names from exported URL"""
    df = pd.read_csv(csv_p)
    return [p for p in df.Titulo.tolist()]

def save_to_elastic(doc, elast, idx, id=None):
    if id is not None:
        res = elast.index(index=idx, id=id, body=doc)
    else:
        res = elast.index(index=idx, body=doc)

    if res['result'] != 'created':
        raise Exception(f'Restaurant <{doc}> was not created.\n Result: <{res}>')
    else:
        return 200

def get_save_detailed_info(place_id, gmaps, elast, idx='restaurants-gordologo-default'):
    # check if document already in DB
    res = elast.get(index=idx, id=place_id, ignore=404)
    if res['found']:
        name = res['_source']['name']
        print(f'Place <{name}> already in DB')
        return 404
    else:
        # get detailed information
        place_doc = gmaps.place(place_id)
        # save to elastic
        return save_to_elastic(place_doc['result'], elast, idx, place_id)

def save_fail_info(place_doc, elast, idx='restaurants-gordologo-fail'):
    # check if document already in DB
    place_id = place_doc['name']
    res = elast.get(index=idx, id=place_id, ignore=404)
    if res['found']:
        name = res['_source']['name']
        print(f'Place <{name}> already in DB')
        return 404
    else:
        # save to elastic
        return save_to_elastic(place_doc, elast, idx, place_id)

def search_name(name, gmaps, elast):
    query = {
        "query_string": {
            "default_field": "name",
            "query": f"\"{name}\""
            }
        }
    # search default index
    res = elast.search(index='restaurants-gordologo-default', 
                       body={"query": query})
    hits = res['hits']['total']['value']

    # search fail index
    res = elast.get(index='restaurants-gordologo-fail', 
                    id=name, ignore=404)

    if hits == 1 or res['found']:
        return {'status': 'EXISTING'}
    # if multiple hits, we are unsure if the match is right, so we search again
    else:
        r = gmaps.find_place(name, 
                             'textquery', 
                             fields=['place_id', 'formatted_address', 'name'])
        return r

def get_places_info_from_names(places_names, gmaps_client, elastic_client):
    """
        Call Google API to get places information.
    """
    for i, place in enumerate(places_names):
        if not i % 10:
            print(f'{i} places processed')
        # search in DB first, then in gmaps API 
        r = search_name(place, gmaps_client, elastic_client)

        # gmaps response, search for detailed info and save it in DB
        if r['status'] in ['OK', 'ZERO_RESULTS']:
            n_candidates = len(r['candidates'])
            if n_candidates == 1:
                place_id = r['candidates'][0]['place_id']
                status = get_save_detailed_info(place_id, gmaps_client, elastic_client)
            # ambiguous candidates or 0 candidates, save it to fail index
            else:
                doc = {'name': place, 'candidates': r['candidates']}
                status = save_fail_info(doc, elastic_client, 'restaurants-gordologo-fail')
        # existing in DB
        elif r['status'] == 'EXISTING':
            print(f'Place <{place}> already in DB')
        else:
            print(f'Unsuccesful request:\n {r}')
            return False
    
    return True

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

    gmaps = googlemaps.Client(key=api_key)
    elast = Elasticsearch('localhost', port=9200)
    val = get_places_info_from_names(places_names, gmaps, elast)
    if not val:
        print("Results not saved due to unsuccessful request")
