import bcrypt

from models.user import UserModel


def authenticate(username, password):
    user = UserModel.find_by_username(username)
    if user and bcrypt.hashpw(password.encode("utf-8"), user.password_hash.encode("utf-8")) == user.password_hash.encode("utf-8"):
        return user

def identity(payload):
    user_id = payload["identity"]
    return UserModel.find_by_id(user_id)
