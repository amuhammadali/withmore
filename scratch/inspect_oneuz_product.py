import urllib.request
from bs4 import BeautifulSoup
import re

url = "https://oneuz.magicbot.store/products/kastyum-shim-over-baxmal-toq-kok-2xl"
headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'}

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, "html.parser")
        
        # Product title and price
        title = soup.find("h1")
        print("Product Title:", title.get_text(strip=True) if title else "None")
        
        # Buttons / options
        buttons = soup.find_all("button")
        print("Buttons:", [b.get_text(strip=True) for b in buttons if b.get_text(strip=True)])
        
        # Text content
        main = soup.find("main") or soup.find("body")
        if main:
            lines = [l.strip() for l in main.get_text(separator="\n").split("\n") if l.strip()]
            print("Main lines snippet:", lines[:30])
except Exception as e:
    print("Err:", e)

