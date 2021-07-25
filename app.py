from flask import Flask, request, render_template
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required
from elasticsearch import Elasticsearch

from security import authenticate, identity

app = Flask(__name__)
app.secret_key = "secret_key"
api = Api(app)

jwt = JWT(app, authenticate, identity) # /auth


class Restaurant(Resource):
    parser = reqparse.RequestParser()
    # add mandatory fields
    
    parser.add_argument("business_status", 
                        type=str, 
                        required=True, 
                        help="This field is mandatory.")
    parser.add_argument("formatted_address", 
                        type=str, 
                        required=True, 
                        help="This field is mandatory.")
    parser.add_argument("geometry", 
                        type=dict, 
                        required=True, 
                        help="This field is mandatory.")
    parser.add_argument("international_phone_number", 
                        type=str, 
                        required=True, 
                        help="This field is mandatory.")
    parser.add_argument("name", 
                        type=str, 
                        required=True, 
                        help="This field is mandatory.")
    parser.add_argument("opening_hours", 
                        type=dict, 
                        required=True, 
                        help="This field is mandatory.")
    parser.add_argument("place_id", 
                        type=str, 
                        required=True, 
                        help="This field is mandatory.")
    parser.add_argument("price_level", 
                        type=int, 
                        required=True, 
                        help="This field is mandatory.")
    parser.add_argument("rating", 
                        type=float, 
                        required=True, 
                        help="This field is mandatory.")
    parser.add_argument("types", 
                        type=list, 
                        required=True, 
                        help="This field is mandatory.")
    parser.add_argument("user_ratings_total", 
                        type=int, 
                        required=True, 
                        help="This field is mandatory.")
    parser.add_argument("website", 
                        type=str, 
                        required=True, 
                        help="This field is mandatory.")

    # add optional fields
    parser.add_argument("address_components", 
                        type=list, 
                        required=False)
    parser.add_argument("formatted_phone_number", 
                        type=str, 
                        required=False)
    parser.add_argument("icon", 
                        type=float, 
                        required=False)
    parser.add_argument("photos", 
                        type=list, 
                        required=False)
    parser.add_argument("plus_code", 
                        type=dict, 
                        required=False)
    parser.add_argument("reviews", 
                        type=list, 
                        required=False)
    parser.add_argument("url", 
                        type=str, 
                        required=False)
    parser.add_argument("utc_offset", 
                        type=int, 
                        required=False)
    parser.add_argument("vicinity", 
                        type=str, 
                        required=False)

    elast = Elasticsearch('localhost', port=9200)
    elast_idx = "gordologo-default"

    @jwt_required()
    def get(self, id_):
        res = Restaurant.elast.get(index=Restaurant.elast_idx, 
                                   id=id_, 
                                   ignore=404)
        if res['found']:
            return {"restaurant": res['_source']}, 200
        else:
            return {"restaurant": None}, 404

    @jwt_required()
    def post(self, id_):
        res = Restaurant.elast.get(index=Restaurant.elast_idx, 
                                   id=id_, 
                                   ignore=404)
        if res['found']:
            return {"message": f"Restaurant '{id_}' already exists"}, 400

        data = Restaurant.parser.parse_args()
        res = Restaurant.elast.index(index=Restaurant.elast_idx, 
                                     id=id_, 
                                     body=data)
        if res['result'] != 'created':
            return {"message": "Internal server error"}, 500
        else:
            return {"restaurant": data}, 201

    @jwt_required()
    def delete(self, id_):
        res = Restaurant.elast.delete(index=Restaurant.elast_idx, 
                                      id=id_,
                                      ignore=404)
        if res["result"] == "deleted":
            return {"message": "Item deleted"}
        else:
            return {"message": "Item not found"}, 404

    @jwt_required()
    def put(self, id_):
        data = Restaurant.parser.parse_args()

        res = Restaurant.elast.get(index=Restaurant.elast_idx, 
                                   id=id_, 
                                   ignore=404)
        found = res['found']

        res = Restaurant.elast.index(index=Restaurant.elast_idx, 
                                     id=id_, 
                                     body=data)
        if (res['result'] == 'created' and not found) or (res['result'] == 'updated' and found):
            return {"restaurant": data}, 201 if not found else 200
        else:
            return {"message": "Internal server error"}, 500


class RestaurantList(Resource):

    parser = reqparse.RequestParser()    
    parser.add_argument("from",
                        type=int, 
                        required=False,
                        default=0)
    parser.add_argument("size",
                        type=int, 
                        required=False,
                        default=10)

    elast = Elasticsearch('localhost', port=9200)
    elast_idx = "restaurants-gordologo-default"

    def get(self):
        data = RestaurantList.parser.parse_args()
        query = {
            "query": {
                "match_all": {}
            },
            "size": data["size"],
            "from": data["from"]
        }
        res = RestaurantList.elast.search(index=RestaurantList.elast_idx, 
                                          body=query)
        restaurants = [r["_source"] for r in res['hits']['hits']]

        return {"restaurants": restaurants}

api.add_resource(Restaurant, "/restaurant/<string:id>")
api.add_resource(RestaurantList, "/restaurants")
app.run(port=5000, debug=True)
