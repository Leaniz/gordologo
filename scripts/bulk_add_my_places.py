import pandas as pd
from add_restaurant import Client, get_user_pwd


def get_places_names(csv_p):
    """get places names from exported URL"""
    df = pd.read_csv(csv_p)
    return [p for p in df.Titulo.tolist()]
def save_to_log(r, p="./log.txt"):
    with open(p, "a") as f:
        f.write(str(r) + "\n")

def bulk_add_restaurants(places_names, client):
    """
        Call Google API to get places information.
    """
    for i, name in enumerate(places_names):
        if not i % 10:
            print(f'{i} places processed')
        res = client.search_add_restaurant(name)
        if res["message"] == "Success":
            pass
        elif "Error" in res["message"]:
            print(f"Error processing '{name}'")
            save_to_log(res)
            continue
        else:
            results = res["results"]
            if len(results) == 0:
                location_bias = input(f"'{name}' not found, please add a location bias separated by commas:")
                lat, lon = location_bias.split(",")
                res = client.search_add_restaurant(name, lat, lon)
                if res["message"] != "Success":
                    print(f"Error processing '{name}'")
                    save_to_log(res)
                    continue
            elif len(results) == 1 and not results[0]["exact_match"]:
                answer = input(f"Is '{name}' this restaurant? (y/n)\n\n{results}")
                if answer.lower() != "y":
                    location_bias = input("Please add a location bias separated by commas:")
                    lat, lon = location_bias.split(",")
                    res = client.search_add_restaurant(name, lat, lon, True)
                    if res["message"] != "Success":
                        print(f"Error processing '{name}'")
                        save_to_log(res)
                        continue
            elif len(results) > 1:
                results_dic = {j: r for j, r in enumerate(results)}
                answer = input((f"Multiple results for '{name}'. Which is the correct restaurant?\n\n"
                                f"{results_dic}"))
                if int(answer) not in results_dic:
                    location_bias = input("Please add a location bias separated by commas:")
                    lat, lon = location_bias.split(",")
                    res = client.search_add_restaurant(name, lat, lon)
                    if res["message"] != "Success":
                        print(f"Error processing '{name}'")
                        save_to_log(res)
                        continue
                else:
                    res = client.add_restaurant(results_dic[int(answer)]["place_id"])
                    if res["message"] != "Success":
                        print(f"Error processing '{name}'")
                        save_to_log(res)
                        continue
            else:
                print(f"Error processing '{name}'")
                save_to_log(res)
                continue
        print(f"'{name}' processed correctly")



if __name__ == '__main__':
    # "Quiero ir" file comes from Google Takeout, selecting "Save" category <https://takeout.google.com/settings/takeout?hl=es>
    input_file = './data/Quiero ir.csv'
    places_names = get_places_names(input_file)

    user, password = get_user_pwd()
    client = Client(user, password)
    bulk_add_restaurants(places_names, client)
