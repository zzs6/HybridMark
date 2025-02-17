import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import re
import ipaddress

import geoip2.database

import requests

import os
import pandas as pd
import pycountry

def get_IP2Location(ip_address):
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=C:")
    chrome_options.add_argument("profile-directory=Default")
    chrome_options.binary_location = "D:\chrome.exe"
    service = Service("D:\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        url = "https://www.ip2location.io/"
        driver.get(url)
        input_field = driver.find_element(By.ID, "ip")
        input_field.clear()
        input_field.send_keys(ip_address)
        input_field.send_keys(Keys.RETURN)
        time.sleep(1)
        pre_element = driver.find_element(By.CSS_SELECTOR, "pre#code")
        json_text = pre_element.text
        data = json.loads(json_text)
        city_name = data["city_name"]
        return city_name

    except Exception as e:
        print(f"{e}")
        return ""

    finally:
        driver.quit()
    
def get_Maxmind(ip_address):
    try:
        with geoip2.database.Reader(r'D:\GeoLite2-City.mmdb') as reader:
            response = reader.city(ip_address)
            print(f"{response.city.name}")
            return response.city.name
    except Exception as e:
        print(f"{e}")
        return ""

def get_geobytes(ip_address):
    try:
        url = f"http://getcitydetails.geobytes.com/GetCityDetails?fqcn={ip_address}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            city = data.get('geobytescity')
            country = data.get('geobytescountry')
            region = data.get('geobytesregion')
        else:
            print(f"{ip_address}")
    except Exception as e:
        print(f"{e}")

def get_ipinfo(ip_address):
    try:
        url = f"https://ipinfo.io/widget/demo/{ip_address}"
        response = requests.get(url)
        data = json.loads(response.text)
        city = data['data']['city']
        return city
    
    except Exception as e:
        print(f"{e}")
        return ""

def validation_fofa_data():
    source_folder = r'D:\research\project\landmark\target\IoT\data'  
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path)
                    for index, row in df.iterrows():
                        ip_address = row['ip']
                        ip_address = "8.8.8.8"
                        #Alpha_2 = row['country']
                        #latitude = row['latitude']
                        #longitude = row['longitude']
                        #country =  pycountry.countries.lookup(Alpha_2).name
                        #extracted_data.append([ip_address, country, Alpha_2, latitude, longitude])
                        IP2Location_result = get_IP2Location(ip_address)
                        Maxmind_result = get_Maxmind(ip_address)
                        #geobytes_result = get_geobytes(ip_address)
                        ipinfo_result = get_ipinfo(ip_address)
                        if IP2Location_result == Maxmind_result == ipinfo_result:
                            print("yes")
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

def get_ipdata_cloud(ip_address):
    try:
        url = f"https://api.ipdatacloud.com/v2/query?ip={ip_address}&key=123456"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            city = data["data"]["location"]["city"]
            return city
        else:
            print(f"{ip_address}")
    except Exception as e:
        print(f"{e}")

