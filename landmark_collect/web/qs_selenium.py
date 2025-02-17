import pandas as pd
import requests
import os
import ollama
from urllib3.exceptions import InsecureRequestWarning
import urllib3


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re


urllib3.disable_warnings(InsecureRequestWarning)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}


file_path = "input.csv" 
output_file = "output_2.csv"
temp_file = "temp_output_2.csv"
LLM = "llama3.1:8b"
que = """Please use your knowledge in conjunction with the above HTML code and text to tell me which university's website it might belong to and provide the possible geographical location (the answer should follow the 'university , address' standard, the answer must consist of only two fields! No need to provide reasons!And pay particular attention to the URL of the webpage itself, as it often contains the correct initials of the university's name.)"""

chrome_options = Options()
chrome_options.binary_location = "D:\software\Google\Chrome\Application\chrome.exe"
service = Service("D:\software\Anaconda\envs\landmark\chromedriver.exe")

driver = webdriver.Chrome(service=service, options=chrome_options)


if os.path.exists(temp_file):
    df = pd.read_csv(temp_file)
else:
    df = pd.read_csv(file_path)
    df["university"] = [None] * df.shape[0]
    df["address"] = [None] * df.shape[0]

for i in range(0, df.shape[0]):
    if pd.notna(df.loc[i, "university"]) and pd.notna(df.loc[i, "address"]):
        continue
    
    selected_column = df.iloc[i, 4]
    num = df.iloc[i,0]
    print(f"{num}  Processing URL: {selected_column}")
    
    try:
        #response = requests.get(selected_column, timeout=10, verify=False, headers=headers)
        driver.get(selected_column)
        html = driver.page_source
        combined_input = "{} \n {} ".format(html, que)
        print("Sending to LLM...")
        
        res = ollama.chat(
            model=LLM,
            stream=False,
            messages=[{"role": "user", "content": combined_input}],
            options={"temperature": 0},
        )
        
        org, addr = res["message"]["content"].split(',', 1)
        org = org.strip()
        addr = addr.strip()
        
        df.loc[i, "university"] = org
        df.loc[i, "address"] = addr
        print(f"Extracted: {org}, {addr}\n")
        df.to_csv(temp_file, index=False)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        continue 

df.to_csv(output_file, index=False)
print(f"Finished processing. Results saved to {output_file}.")
