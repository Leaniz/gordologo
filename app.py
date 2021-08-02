from flask import Flask
from flask_restful import Api
from flask_jwt import JWT
from datetime import timedelta

from security import authenticate, identity
from resources.user import UserRegister
from resources.restaurant import Restaurant, RestaurantList, RestaurantImportModel

app = Flask(__name__)
app.secret_key = "secret_key"
api = Api(app)

jwt = JWT(app, authenticate, identity) # /auth

api.add_resource(Restaurant, "/restaurant/<string:place_id>")
api.add_resource(RestaurantList, "/restaurants")
api.add_resource(UserRegister, "/register")
api.add_resource(RestaurantImportModel, "/find")

# config JWT to expire within half an hour
app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=1800)

app.run(port=5000, debug=True)
