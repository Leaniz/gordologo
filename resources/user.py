from flask_restful import Resource, reqparse
from elasticsearch import Elasticsearch
import bcrypt

from models.user import UserModel


class UserRegister(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("username",
        type=str,
        required=True,
        help="This field cannot be blank."
    )
    parser.add_argument("email",
        type=str,
        required=True,
        help="This field cannot be blank."
    )
    parser.add_argument("password",
        type=str,
        required=True,
        help="This field cannot be blank."
    )
    
    elast = Elasticsearch('localhost', port=9200)
    elast_idx = "gordologo-users"

    def post(self):
        data = UserRegister.parser.parse_args()

        user = UserModel.find_by_email(data["email"])
        if user:
            return {"message": f"Email already in use"}, 400

        user = UserModel.find_by_username(data["username"])
        if user:
            return {"message": f"Username already in use"}, 400

        user = {
            "username": data["username"],
            "email": data["email"],
            "password_hash": bcrypt.hashpw(data["password"].encode("utf-8"), 
                                           bcrypt.gensalt()).decode("utf-8")
        }

        res = UserRegister.elast.index(index=UserRegister.elast_idx,
                                       body=user)
        if res['result'] != 'created':
            return {"message": "Internal server error"}, 500
        else:
            user.pop("password_hash")
            user["id"] = res["_id"]
            return {"user": user}, 201


