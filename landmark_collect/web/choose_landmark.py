import whois
import requests
import dns.resolver
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re
import ipaddress

import base64
import pycountry

import pandas as pd
import os

def whois_info(domain):
    try:
        domain_info = whois.whois(domain)        
        return domain_info

    except Exception as e:
        print(f"An error occurred: {e}")

def http_head(url):
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.binary_location = "D:\software\Google\Chrome\Application\chrome.exe"
    chrome_options.add_argument("user-data-dir=C:/Users/zzs/AppData/Local/Google/Chrome/User Data")
    chrome_options.add_argument("profile-directory=Default") 

    service = Service("D:\software\Anaconda\envs\landmark\chromedriver.exe")


    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        driver.get(url)

        headers = driver.execute_script("""
            var xhr = new XMLHttpRequest(); xhr.open('HEAD', arguments[0], false); xhr.send(null);
            return {
                'X-Cache': xhr.getResponseHeader('X-Cache'),
                'Via': xhr.getResponseHeader('Via'),
                'Server': xhr.getResponseHeader('Server'),
                'X-CDN': xhr.getResponseHeader('X-CDN'),
            };
        """, url)
        return headers


    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def http_head_requests(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.127 Safari/537.36"
    }
    try:
        response = requests.head(url, headers=headers, verify=True, timeout=10)
        return {
            'X-Cache': response.headers.get('X-Cache'),
            'Via': response.headers.get('Via'),
            'Server': response.headers.get('Server'),
            'X-CDN': response.headers.get('X-CDN'),
        }
    except requests.RequestException as e:
        print(f"Error fetching headers for {url}: {e}")
        return None

def dns_infoget(domain):
    info = {}
    try:
        answers = dns.resolver.resolve(domain, 'CNAME')
        for rdata in answers:
            #print(f'CNAME record: {rdata.target}')
            info['CNAME'] = rdata.target

    except dns.resolver.NoAnswer:
        #print(f'No CNAME record found for {domain}')
        info['CNAME'] = ""
    except Exception as e:
        #print(f'An error occurred: {e}')
        info['CNAME'] = ""


    try:
        answers = dns.resolver.resolve(domain, 'MX')
        for rdata in answers:
            #print(f'MX record: {rdata.exchange}, Priority: {rdata.preference}')
            info['MX'] = rdata.exchange

    except dns.resolver.NoAnswer:
        #print(f'No MX record found for {domain}')
        info['MX'] = ""
    except Exception as e:
        #print(f'An error occurred: {e}')
        info['MX'] = ""
    return info

def rdns_infoget(ip_address):
    try:
        reversed_dns = dns.reversename.from_address(ip_address)
        answer = dns.resolver.resolve(reversed_dns, 'PTR')
        for rdata in answer:
            print(f'PTR record (reverse DNS): {rdata.target}')
            return rdata.target

    except dns.resolver.NoAnswer:
        print(f'No PTR record found for {ip_address}')
        return ""
    except Exception as e:
        print(f'An error occurred: {e}')
        return ""

def A_record_get(domain):
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=C:/Users/zzs/AppData/Local/Google/Chrome/User Data")
    chrome_options.add_argument("profile-directory=Default")
    chrome_options.binary_location = "D:\software\Google\Chrome\Application\chrome.exe"
    service = Service("D:\software\Anaconda\envs\landmark\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        url = "https://dnschecker.org/#A/"
        driver.get(url+domain)
        time.sleep(2)
        button = driver.find_element(By.ID, "s")
        button.click()
        time.sleep(5)
        new_content = driver.page_source
        td_elements = driver.find_elements(By.CSS_SELECTOR, "td.align-middle.small.font-weight-light.text_blue.text-end.result")
        ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
        ip_addresses = set()
        for td in td_elements:
            text = td.text 
            ips = ip_pattern.findall(text) 
            ip_addresses.update(ips)
        for ip in ip_addresses:
            print(ip)
        return ip_addresses
    finally:
        driver.quit()

def Fofa_get(ip_address):
    url = "https://fofa.info/api/v1/search/all?"
    original_string = f'ip="{ip_address}"'
    bytes_string = original_string.encode("utf-8")
    base64_bytes = base64.b64encode(bytes_string)
    base64_string = base64_bytes.decode("utf-8")
    request_parameters = f"key=2a042d0944eaae0a45304e23f99a1504&qbase64={base64_string}&fields=ip,country,country_name&size=1"
    request_url = url + request_parameters
    response = requests.get(request_url)
    try: 
        data = response.json()
        return data['results'][0][1]
        #print(data)
    except:
        print("Fofa貌似没返回查找结果...")

def get_country_code(country_name):
    country = pycountry.countries.get(name=country_name)
    if country:
        return country.alpha_2
    else:
        return None

def poi_info(university_name, address):
    proxies = {
        "http": "socks5://127.0.0.1:10808",
        "https": "socks5://127.0.0.1:10808"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    q = f"{university_name} {address}"
    oq = f"{university_name} {address}"
    url = f"https://www.google.com.hk/search?tbm=map&authuser=0&hl=en&gl=in&pb=!4m12!1m3!1d3123.48603172887!2d139.7266564756444!3d35.660452272594!2m3!1f0!2f0!3f0!3m2!1i766!2i740!4f13.1!7i20!10b1!12m20!1m2!18b1!30b1!2m3!5m1!6e2!20e3!10b1!12b1!13b1!16b1!17m1!3e1!20m3!5e2!6b1!14b1!46m1!1b0!94b1!19m4!2m3!1i360!2i120!4i8!20m57!2m2!1i203!2i100!3m2!2i4!5b1!6m6!1m2!1i86!2i86!1m2!1i408!2i240!7m42!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!2b1!4b1!9b0!22m6!1shDDQZqeyJt3B0PEPg5uguQM%3A5!2s1i%3A0%2Ct%3A11887%2Cp%3AhDDQZqeyJt3B0PEPg5uguQM%3A5!7e81!12e3!17shDDQZqeyJt3B0PEPg5uguQM%3A457!18e15!24m96!1m31!13m9!2b1!3b1!4b1!6i1!8b1!9b1!14b1!20b1!25b1!18m20!3b1!4b1!5b1!6b1!9b1!12b1!13b1!14b1!17b1!20b1!21b1!22b1!25b1!27m1!1b0!28b0!31b0!32b0!33m1!1b0!10m1!8e3!11m1!3e1!14m1!3b0!17b1!20m2!1e3!1e6!24b1!25b1!26b1!29b1!30m1!2b1!36b1!39m3!2m2!2i1!3i1!43b1!52b1!54m1!1b1!55b1!56m1!1b1!65m5!3m4!1m3!1m2!1i224!2i298!71b1!72m19!1m5!1b1!2b1!3b1!5b1!7b1!4b1!8m10!1m6!4m1!1e1!4m1!1e3!4m1!1e4!3sother_user_reviews!6m1!1e1!9b1!89b1!103b1!113b1!117b1!122m1!1b1!125b0!126b1!127b1!26m4!2m3!1i80!2i92!4i8!30m0!34m18!2b1!3b1!4b1!6b1!8m6!1b1!3b1!4b1!5b1!6b1!7b1!9b1!12b1!14b1!20b1!23b1!25b1!26b1!37m1!1e81!42b1!47m0!49m9!3b1!6m2!1b1!2b1!7m2!1e3!2b1!8b1!9b1!50m4!2e2!3m2!1b1!3b1!67m3!7b1!10b1!14b1!69i704&q={q}&oq={oq}gs_l=maps.12...0.0.12.20349.0.0.....0.0..0.....0......maps..0.0.0.0.&tch=1&ech=12&psi=hDDQZqeyJt3B0PEPg5uguQM.1724919943624.1"
    resp = requests.get(url, headers=headers, proxies=proxies)
    dir = re.compile(r'null,null,(?P<dire>(?:[-+]?[1-9]\d*|[-+]?0)\.\d*,(?:[-+]?[1-9]\d*|[-+]?0)\.\d*)]')
    match = dir.search(resp.text)
    
    if match:
        return match.group('dire')
    else:
        return None

def evalue(domain, url, ip_address, country):
    islandmark = 1
    black_list = [
    "Google", "Amazon", "Microsoft Azure", "IBM Cloud", "Oracle Cloud", "DigitalOcean", "Linode", "Vultr", "Akamai", 
    "Cloudflare", "Fastly", "CDNetworks", "Verizon Media", "Lumen Technologies", "StackPath", "Rackspace", 
    "Facebook", "Apple", "Salesforce", "Dropbox", "Netlify", "GitHub", "Heroku", "Squarespace"
]
    whois_response = whois_info(domain)
    if whois_response is None:
        print("Unable to fetch WHOIS information")    
    whois_text = str(whois_response).lower()
    black_list_lower = [term.lower() for term in black_list]    
    found_blacklist_terms = [term for term in black_list_lower if term in whois_text]
    if found_blacklist_terms:
        print(f"Blacklist terms found in whois: {found_blacklist_terms}")
        islandmark = 0
    else:
        print("No blacklist terms found in whois")


    http_head_info = http_head_requests(url)
    if http_head_info:
        if 'X-Cache' in http_head_info and http_head_info['X-Cache'] :
            islandmark = 0
            print("X-Cache : ",http_head_info['X-Cache'])
        if 'Via' in http_head_info and http_head_info['Via']:
            islandmark = 0
            print("Via : ",http_head_info['Via'])
        if 'X-CDN' in http_head_info and http_head_info['X-CDN']:
            islandmark = 0
            print("X-CDN : ",http_head_info['X-CDN'])
        found_blacklist_terms = [term for term in black_list_lower if http_head_info.get('Server') is not None and term in http_head_info['Server']]
        if found_blacklist_terms:
            print(f"Blacklist terms found in http_headers: {found_blacklist_terms}")
            islandmark = 0


    dns_info = dns_infoget(domain)
    found_blacklist_terms = [term for term in black_list_lower if term in dns_info['CNAME'] or term in dns_info['MX']]
    if found_blacklist_terms:
        print(f"Blacklist terms found in dns_info: {found_blacklist_terms}")
        islandmark = 0
    rdns_info = rdns_infoget(ip_address)
    found_blacklist_terms = [term for term in black_list_lower if term in rdns_info]
    if found_blacklist_terms:
        print(f"Blacklist terms found in rdns: {found_blacklist_terms}")
        islandmark = 0

    ip_set = set()
    A_record = A_record_get(domain)
    if not A_record:
        print("no A record")
    for ip in A_record:
        try:
            ip_add = ipaddress.ip_network(f'{ip}/{8}', strict=False)
            ip_set.add(ip_add)
        except ValueError:
            print(f'Invalid IP address: {ip}')
            return False
    if len(ip_set) > 1:
        islandmark = 0
