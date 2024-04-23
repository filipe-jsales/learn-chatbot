import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

class TxtCreator:
    def __init__(self, base_url):
        self.base_url = base_url
        self.urls = []

    def get_urls(self):
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()  # Raise an error for non-200 status codes
            soup = BeautifulSoup(response.text, "html.parser")
            header_content = soup.find("header")
            links = header_content.find_all("a")
            for link in links:
                link_url = urljoin(self.base_url, link['href'].replace("#", ""))
                self.urls.append(link_url)
        except requests.RequestException as e:
            print(f"An error occurred while fetching URLs: {e}")

    def create_txt(self):
        content = ""  # Initialize content variable
        for url in self.urls:
            try:
                response = requests.get(url)
                response.raise_for_status()  
                soup = BeautifulSoup(response.text, "html.parser")
                text = soup.find("main").getText("\n") + "\n\n"
                content += text.strip()
            except requests.RequestException as e:
                print(f"An error occurred while processing URL {url}: {e}")
        
        try:
            with open("data/data.txt", "w") as f:
                f.write(content)
        except IOError as e:
            print(f"An error occurred while writing content to file: {e}")
            
    def run(self):
        self.get_urls()
        self.create_txt()

# Usage

