import json
import pandas as pd
import ipaddress
import subprocess
import csv
import os


def ping_ip(ip):
    try:
        result = subprocess.run(['ping', '-n', '1', str(ip)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1)
        return result.returncode == 0
    except Exception as e:
        return False


def save_to_csv(ip, location, csv_filename='reachable_ips.csv'):
    file_exists = os.path.isfile(csv_filename)

    with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['ip_address', 'location'])
        writer.writerow([ip, location])

def test_ip_range(cidr, location):
    ip_network = ipaddress.ip_network(cidr)
    ping_count = 0
    for ip in ip_network.hosts(): 
        if ping_ip(ip):
            save_to_csv(ip, location)
            ping_count += 1
        else:
            print("no")

        if ping_count == 2:
            break


csv_file = 'microsoft_datacenter_info.csv' 
csv_data = pd.read_csv(csv_file)

region_location_dict = dict(zip(csv_data['region_name'], csv_data['location']))
json_file = 'ServiceTags_Public_20240909.json'
with open(json_file, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

for value in json_data.get('values', []):
    properties = value.get('properties')
    if not properties:
        continue
    region_name = properties.get('region')

    if region_name in region_location_dict:
        location = region_location_dict[region_name]
        address_prefixes = properties.get('addressPrefixes', [])

        for address in address_prefixes:
            print(f"Region: {region_name}, Location: {location}, Address: {address}")
            network = ipaddress.ip_network(address, strict=False)
            if isinstance(network,ipaddress.IPv4Network):
                test_ip_range(address, location)
