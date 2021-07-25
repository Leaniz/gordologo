from flask_restful import Resource, reqparse

class User:
    def __init__(self, _id, username, password):
        self.id = _id
        self.username = username
        self.password = password

    @classmethod
    def find_by_username(cls, username):
        user = cls(1, "Pepe", "asdf")
        return user

    @classmethod
    def find_by_id(cls, id_):
        user = cls(1, "Pepe", "asdf")
        return user


class UserRegister(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("email",
        type=str,
        required=True,
        help="This field cannot be blank."
    )

    def post(self):
        data = UserRegister.parser.parse_args()


