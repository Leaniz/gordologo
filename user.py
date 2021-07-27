from flask_restful import Resource, reqparse
from elasticsearch import Elasticsearch
import bcrypt
from flask_jwt import jwt_required

class User:

    elast = Elasticsearch('localhost', port=9200)
    elast_idx = "gordologo-users"

    def __init__(self, _id, username, email, password_hash):
        self.id = _id
        self.username = username
        self.email = email
        self.password_hash = password_hash

    def to_dict(self):
        d = {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }
        return d

    @classmethod
    def find_by_username(cls, username):
        query = {
            "query": {
                "term": {
                    "username.keyword": {
                        "value": username,
                        "case_insensitive": True
                    }
                }
            }
        }
        res = User.elast.search(index=User.elast_idx, 
                                body=query)
        hits = res["hits"]["hits"]
        if len(hits):
            user_dict = hits[0]["_source"]
            user_dict["_id"] = hits[0]["_id"]
            return cls(**user_dict)
        else:
            return None

    @classmethod
    def find_by_email(cls, email):
        query = {
            "query": {
                "term": {
                    "email.keyword": {
                        "value": email,
                        "case_insensitive": True
                    }
                }
            }
        }
        res = User.elast.search(index=User.elast_idx, 
                                body=query)
        hits = res["hits"]["hits"]

        if len(hits):
            user_dict = hits[0]["_source"]
            user_dict["_id"] = hits[0]["_id"]
            return cls(**user_dict)
        else:
            return None

    @classmethod
    def find_by_id(cls, id_):
        res = User.elast.get(index=User.elast_idx, 
                             id=id_, 
                             ignore=404)
        if res["found"]:
            user_dict = res["_source"]
            user_dict["_id"] = res["_id"]
            return cls(**user_dict)
        else:
            return None


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

    @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("id",
            type=str,
            required=True,
            help="This field cannot be blank."
        )

        data = parser.parse_args()

        user = User.find_by_id(data["id"])
        if user:
            return {"user": user.to_dict()}, 200
        else:
            return {"user": user}, 404

    def post(self):
        data = UserRegister.parser.parse_args()

        user = User.find_by_email(data["email"])
        if user:
            return {"message": f"Email already in use"}, 400

        user = User.find_by_username(data["username"])
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


