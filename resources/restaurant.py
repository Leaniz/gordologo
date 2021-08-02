from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

from models.restaurant import RestaurantModel, RestaurantImportModel


class Restaurant(Resource):
    parser = reqparse.RequestParser()
    # add mandatory field
    parser.add_argument("name", 
                        type=str, 
                        required=True, 
                        help="This field is mandatory.")

    # add optional but important fields
    parser.add_argument("business_status", 
                        type=str, 
                        required=False)
    parser.add_argument("formatted_address", 
                        type=str, 
                        required=False)
    parser.add_argument("geometry", 
                        type=dict, 
                        required=False)
    parser.add_argument("international_phone_number", 
                        type=str, 
                        required=False)
    parser.add_argument("opening_hours", 
                        type=dict, 
                        required=False)
    parser.add_argument("price_level", 
                        type=int, 
                        required=False)
    parser.add_argument("rating", 
                        type=float, 
                        required=False)
    parser.add_argument("types", 
                        type=list, 
                        required=False)
    parser.add_argument("user_ratings_total", 
                        type=int, 
                        required=False)
    parser.add_argument("website", 
                        type=str, 
                        required=False)

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

    @jwt_required()
    def get(self, place_id):
        restaurant = RestaurantModel.find_by_id(place_id)
        if restaurant:
            return {"restaurant": restaurant.to_dict()}, 200
        else:
            return {"restaurant": None}, 404

    @jwt_required()
    def post(self, place_id):
        if RestaurantModel.find_by_id(place_id):
            return {"message": f"Restaurant '{place_id}' already exists"}, 400

        data = Restaurant.parser.parse_args()
        data["place_id"] = place_id
        restaurant = RestaurantModel(**data)
        res = restaurant.validate_data()
        if "error" not in res:
            res = restaurant.save_to_db()
            if res != 'created':
                return {"message": "Internal server error"}, 500
            else:
                return {"restaurant": restaurant.to_dict()}, 201
        else:
            print(res)
            return {"message": "Internal server error"}, 500

    @jwt_required()
    def delete(self, place_id):
        res = RestaurantModel.delete_from_db(place_id)
        if res == "deleted":
            return {"message": "Item deleted"}, 200
        else:
            return {"message": "Item not found"}, 404

    @jwt_required()
    def put(self, place_id):
        data = Restaurant.parser.parse_args()
        data["place_id"] = place_id

        found = True if RestaurantModel.find_by_id(place_id) is not None else False

        restaurant = RestaurantModel(**data)
        res = restaurant.validate_data()
        if "error" not in res:
            res = restaurant.save_to_db()

            if (res == 'created' and not found) or (res == 'updated' and found):
                response = {"restaurant": restaurant.to_dict()}
                if found:
                    return response, 200
                else:
                    return response, 201
            else:
                return {"message": "Internal server error"}, 500
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

    @jwt_required()
    def get(self):
        data = RestaurantList.parser.parse_args()
        data["from_"] = data.pop("from")
        
        restaurants = RestaurantModel.find_all(**data)

        return {"restaurants": restaurants}


class RestaurantImport(Resource):

    parser = reqparse.RequestParser()    
    parser.add_argument("name",
                        type=str, 
                        required=True,
                        help="This field is mandatory.")
    parser.add_argument("force_gmaps",
                        type=bool, 
                        required=False,
                        default=False)

    @jwt_required()
    def get(self):
        data = RestaurantImport.parser.parse_args()
        name = data["name"]

        res = RestaurantModel.find_by_name(name)
        if data["force_gmaps"] or len(res["results"]) == 0:
            print("Searching in gmaps")
            restaurant_import = RestaurantImportModel(name)
            res = restaurant_import.find_in_gmaps()

        return res
