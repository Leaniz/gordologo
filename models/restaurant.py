from elasticsearch import Elasticsearch
import googlemaps
from unidecode import unidecode


class RestaurantModel:

    elast = Elasticsearch("localhost", port=9200)
    elast_idx = "gordologo-restaurants"

    with open("./api_key.txt", "r") as f:
        api_key = f.read()
    gmaps = googlemaps.Client(key=api_key)

    def __init__(self, name, place_id=None, 
                 business_status=None, formatted_address=None,
                 geometry=None, international_phone_number=None,
                 opening_hours=None, price_level=None,
                 rating=None, types=None, user_ratings_total=None, 
                 website=None, address_components=None, 
                 formatted_phone_number=None, icon=None, 
                 photos=None, plus_code=None, reviews=None,
                 url=None, utc_offset=None, vicinity=None):

        self.name = name
        self.place_id = place_id
        self.business_status = business_status
        self.formatted_address = formatted_address
        self.geometry = geometry
        self.international_phone_number = international_phone_number
        self.opening_hours = opening_hours
        self.price_level = price_level
        self.rating = rating
        self.types = types
        self.user_ratings_total = user_ratings_total
        self.website = website
        self.address_components = address_components
        self.formatted_phone_number = formatted_phone_number
        self.icon = icon
        self.photos = photos
        self.plus_code = plus_code
        self.reviews = reviews
        self.url = url
        self.utc_offset = utc_offset
        self.vicinity = vicinity

    def from_dict(self, d):
        self.name = d.get("name")
        self.place_id = d.get("place_id")
        self.business_status = d.get("business_status")
        self.formatted_address = d.get("formatted_address")
        self.geometry = d.get("geometry")
        self.international_phone_number = d.get("international_phone_number")
        self.opening_hours = d.get("opening_hours")
        self.price_level = d.get("price_level")
        self.rating = d.get("rating")
        self.types = d.get("types")
        self.user_ratings_total = d.get("user_ratings_total")
        self.website = d.get("website")
        self.address_components = d.get("address_components")
        self.formatted_phone_number = d.get("formatted_phone_number")
        self.icon = d.get("icon")
        self.photos = d.get("photos")
        self.plus_code = d.get("plus_code")
        self.reviews = d.get("reviews")
        self.url = d.get("url")
        self.utc_offset = d.get("utc_offset")
        self.vicinity = d.get("vicinity")

    def to_dict(self):
        d = {
            "name": self.name,
            "place_id": self.place_id,
            "business_status": self.business_status,
            "formatted_address": self.formatted_address,
            "geometry": self.geometry,
            "international_phone_number": self.international_phone_number,
            "opening_hours": self.opening_hours,
            "price_level": self.price_level,
            "rating": self.rating,
            "types": self.types,
            "user_ratings_total": self.user_ratings_total,
            "website": self.website,
            "address_components": self.address_components,
            "formatted_phone_number": self.formatted_phone_number,
            "icon": self.icon,
            "photos": self.photos,
            "plus_code": self.plus_code,
            "reviews": self.reviews,
            "url": self.url,
            "utc_offset": self.utc_offset,
            "vicinity": self.vicinity
        }
        return d

    @classmethod
    def find_by_id(cls, id_):
        res = RestaurantModel.elast.get(index=RestaurantModel.elast_idx, 
                                   id=id_, 
                                   ignore=404)
        return cls(**res["_source"]) if res["found"] else None

    @classmethod
    def find_by_name(cls, name):
        query = {
            "query": {
                "match": {
                    "name": {
                        "query": name,
                        "operator": "AND",
                        "fuzziness": 1
                    }
                }
            }
        }
        res = RestaurantModel.elast.search(index=RestaurantModel.elast_idx, 
                                           body=query)
        restaurants = [r["_source"] for r in res["hits"]["hits"]]

        return {"results": restaurants}

    def save_to_db(self):
        if self.place_id:
            res = RestaurantModel.elast.index(index=RestaurantModel.elast_idx, 
                                        id=self.place_id, 
                                        body=self.to_dict())
        else:
            res = {"result": {"error": "Restaurant has no ID"}}
        return res["result"]

    @classmethod
    def delete_from_db(cls, id_):
        res = RestaurantModel.elast.delete(index=RestaurantModel.elast_idx, 
                                      id=id_,
                                      ignore=404)
        return res["result"]

    @classmethod
    def find_all(cls, size, from_):
        query = {
            "query": {
                "match_all": {}
            },
            "size": size,
            "from": from_
        }
        res = RestaurantModel.elast.search(index=RestaurantModel.elast_idx, 
                                          body=query)
        restaurants = [r["_source"] for r in res["hits"]["hits"]]

        return restaurants

    def validate_data(self, minimum_fields=["name", "price_level", "rating", "formatted_address"]):
        json_data = self.to_dict()
        min_fields_values = [json_data[f] is None for f in minimum_fields]
        if any(min_fields_values):
            res = self.update_info_from_gmaps()
            return res
        else:
            return {"message": "Data was not updated"}

    def update_info_from_gmaps(self):
        # get detailed information
        place_doc = RestaurantModel.gmaps.place(self.place_id)
        try:
            self.from_dict(place_doc["result"])
            response = {"message": "Data was updated from Google"}
        except Exception as e:
            response = {"error": f"Data was not updated. \n Error msg: {e}"}
        finally:
            return response


class RestaurantImportModel:

    elast = Elasticsearch("localhost", port=9200)
    elast_idx = "gordologo-restaurants"

    with open("./api_key.txt", "r") as f:
        api_key = f.read()
    gmaps = googlemaps.Client(key=api_key)

    def __init__(self, name):
        self.name = name

    def find_in_gmaps(self, loc_bias=None):
        location_bias = f"point:{loc_bias['lat']},{loc_bias['lon']}" if loc_bias else None
        r = RestaurantImportModel.gmaps.find_place(
            self.name, 
            "textquery", 
            fields=["place_id", "formatted_address", "name", "price_level", "rating"],
            location_bias=location_bias
            )

        if r["status"] == "OK":
            output = {"results": r["candidates"]}
            for restaurant in output["results"]:
                restaurant["exact_match"] = self.compare_name(self.name, restaurant["name"])
            return output
        elif r["status"] == "ZERO_RESULTS":
            return {"message": "No results found"}
        else:
            return {"message": "Internal server error"}, 500

    def compare_name(self, name_1, name_2):
        name_1 = unidecode(name_1).lower()
        name_2 = unidecode(name_2).lower()
        return name_1 == name_2
