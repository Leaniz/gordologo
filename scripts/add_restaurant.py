import requests
from requests.api import request


def get_user_pwd(p="./user_pwd.txt"):
    with open(p, "r") as f:
        data = f.read()
    data = data.split("\n")

    return data[0], data[1]


class Client:
    def __init__(self, user, password, url="http://127.0.0.1:5000"):
        self.user = user
        self.password = password
        self.url = url
        self.jwt_token = ""

    def auth(self):
        r = requests.post(self.url + "/auth", 
                          json={"username": self.user, "password": self.password})
        r_json = r.json()
        self.jwt_token = r_json.get("access_token")

    def renew_access_token(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except requests.exceptions.HTTPError:
                # Invoke the code responsible for get a new token
                self.auth()
                # once the token is refreshed, we can retry the operation
                return func(self, *args, **kwargs)
        return wrapper

    @renew_access_token
    def add_restaurant(self, place_id):
        r = requests.post(self.url + f"/restaurant/{place_id}",
                          headers={"Authorization": f"JWT {self.jwt_token}"})
        if r.status_code == 201:
            return {"message": "Success", "response": r.json()}
        elif r.status_code == 401:
            raise r.raise_for_status()
        elif r.status_code == 400:
            data = r.json()
            if place_id in data["message"]:
                return {"message": "Success", "response": data}
            else:
                return {"message": "Error", "response": data}
        else:
            return {"message": "Error adding new restaurant", 
                    "status_code": r.status_code, 
                    "response": r.text}

    @renew_access_token
    def search_add_restaurant(self, name, lat=None, lon=None, force_gmaps=False):
        body = {
            "name": name
        }
        if lat and lon:
            body["location_bias"] = {
                    "lat": float(lat),
                    "lon": float(lon)
                }
        if force_gmaps:
            body["force_gmaps"] = True
        r = requests.post(self.url + "/find", 
                          json=body,
                          headers={"Authorization": f"JWT {self.jwt_token}"})
        if r.status_code == 200:
            data = r.json()
            if len(data["results"]) == 1 and data["results"][0]["exact_match"]:
                place_id = data["results"][0]["place_id"]
                return self.add_restaurant(place_id)
            else:
                return {"message": "Ambiguous or empty result", "results": data["results"]}
        elif r.status_code == 401:
            raise r.raise_for_status()
        else:
            return {"message": "Error searching for restaurant",
                    "status_code": r.status_code, 
                    "response": r.text}


if __name__ == "__main__":
    user, password = get_user_pwd()
    client = Client(user, password)
    print(client.search_add_restaurant("tailandes"))
