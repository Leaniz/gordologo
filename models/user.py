from elasticsearch import Elasticsearch

class UserModel:

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
        res = UserModel.elast.search(index=UserModel.elast_idx, 
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
        res = UserModel.elast.search(index=UserModel.elast_idx, 
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
        res = UserModel.elast.get(index=UserModel.elast_idx, 
                             id=id_, 
                             ignore=404)
        if res["found"]:
            user_dict = res["_source"]
            user_dict["_id"] = res["_id"]
            return cls(**user_dict)
        else:
            return None
