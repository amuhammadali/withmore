import urllib.request
from bs4 import BeautifulSoup
import re

headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'}

for path in ['/pages/about', '/pages/delivery', '/pages/contacts']:
    url = f"https://oneuz.magicbot.store{path}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, "html.parser")
            main = soup.find("main") or soup.find("body")
            text = main.get_text(separator="\n", strip=True) if main else ""
            print(f"=== {path} ===")
            print(text[:800])
            print("\n" + "="*40 + "\n")
    except Exception as e:
        print(f"Failed {path}: {e}")

