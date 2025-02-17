import base64
import requests
import fofa
import csv
import iso3166
import os
import pandas as pd
import pycountry

def Fofa_get_ip_request(ip_address):
    url = "https://fofa.info/api/v1/search/all?"
    original_string = f'ip="{ip_address}"'
    bytes_string = original_string.encode("utf-8")
    base64_bytes = base64.b64encode(bytes_string)
    base64_string = base64_bytes.decode("utf-8")

    request_parameters = f"key=123456={base64_string}&fields=ip,country,country_name,latitude,longitude&size=1"
    request_url = url + request_parameters
    response = requests.get(request_url)

    try: 
        data = response.json()
        print(data)
        return data['results'][0][1]
    except:
        print("wrong")

def Fofa_get_request(original_string):
    url = "https://fofa.info/api/v1/search/next?"
    bytes_string = original_string.encode("utf-8")
    base64_bytes = base64.b64encode(bytes_string)
    base64_string = base64_bytes.decode("utf-8")

    request_parameters = f"key=123456={base64_string}&fields=ip,country,country_name,latitude,longitude&size=10"
    request_url = url + request_parameters
    response = requests.get(request_url)

    try: 
        data = response.json()
        print(data)
        return data['results'][0][1]
    except:
        print("wrong")

def Fofa_get_info(target,country):
    key = '123456'
    client = fofa.Client(key=key,email="user@mail.com")
    query_str = f'app="{target}" && country="{country}"'

    folder_name = f'fofa_data_{target}'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    file_path = os.path.join(folder_name, f'fofa_data_{target}_{country}.csv')

    with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(["ip", "country", "country_name", "region", "city", "latitude", "longitude"])
        for page in range(1, 2):
            data = client.search(query_str, size=10000, page=page, fields="ip,country,country_name,region,city,latitude,longitude")
            for ip, country, country_name, region, city, latitude, longitude in data["results"]:
                writer.writerow([ip, country, country_name, region, city, latitude, longitude])


FOFA_EMAIL = "username"
FOFA_KEY = "password"

client = fofa.Client(FOFA_EMAIL, FOFA_KEY)

def get_cities_by_country(alpha_2):
    GEO_NAMES_USERNAME = "username"
    url = f"http://api.geonames.org/searchJSON"
    params = {
        "username": GEO_NAMES_USERNAME,
        "country": alpha_2,
        "featureClass": "P",
        "maxRows": 1000,
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        cities = [entry["name"] for entry in data.get("geonames", [])]
        return list(set(cities))
    
    except Exception as e:
        return []

def search_country_city_nodes(alpha_2_list, max_results_per_city=100, output_file=r"D:"):
    output_data = []

    for alpha_2 in alpha_2_list:
        try:
            country_name = pycountry.countries.lookup(alpha_2).name
            cities = get_cities_by_country(alpha_2)
            for city in cities:
                city_query = f'country="{alpha_2}" && city="{city}"'
                try:
                    city_results = client.search(
                        city_query,
                        size=max_results_per_city,
                        fields="ip,country_name,region,city,latitude,longitude"
                    )
                    for record in city_results["results"]:
                        ip, country, region, city_name, latitude, longitude = record
                        output_data.append({
                            "IP_address": ip,
                            "Country": country,
                            "Alpha_2": alpha_2,
                            "City": city_name,
                            "Latitude": latitude,
                            "Longitude": longitude
                        })
                except Exception as e:
                    print(f"{e}")

        except Exception as e:
            print(f"{e}")

    df = pd.DataFrame(output_data)
    df.to_csv(output_file, index=False, columns=["IP_address", "Country", "Alpha_2", "City", "Latitude", "Longitude"])

