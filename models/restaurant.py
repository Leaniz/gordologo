from elasticsearch import Elasticsearch


class RestaurantModel:

    elast = Elasticsearch('localhost', port=9200)
    elast_idx = "gordologo-restaurants"

    def __init__(self, name, place_id, 
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
        return cls(**res["_source"]) if res['found'] else None

    def save_to_db(self):
        res = RestaurantModel.elast.index(index=RestaurantModel.elast_idx, 
                                     id=self.place_id, 
                                     body=self.to_dict())
        return res['result']

    @classmethod
    def delete_from_db(self, id_):
        res = RestaurantModel.elast.delete(index=RestaurantModel.elast_idx, 
                                      id=id_,
                                      ignore=404)
        return res["result"]

    @classmethod
    def find_all(self, size, from_):
        query = {
            "query": {
                "match_all": {}
            },
            "size": size,
            "from": from_
        }
        res = RestaurantModel.elast.search(index=RestaurantModel.elast_idx, 
                                          body=query)
        restaurants = [r["_source"] for r in res['hits']['hits']]

        return restaurants
