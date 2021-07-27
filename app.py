from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from security import authenticate, identity
from resources.user import UserRegister
from resources.restaurant import Restaurant, RestaurantList

app = Flask(__name__)
app.secret_key = "secret_key"
api = Api(app)

jwt = JWT(app, authenticate, identity) # /auth

api.add_resource(Restaurant, "/restaurant/<string:place_id>")
api.add_resource(RestaurantList, "/restaurants")
api.add_resource(UserRegister, "/register")
app.run(port=5000, debug=True)
