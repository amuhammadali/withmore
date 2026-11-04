import urllib.request
import re

url = 'https://t.me/One23uzbot'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        # find any links or text
        clean = re.sub(r'<[^>]+>', ' ', html)
        clean = ' '.join(clean.split())
        print("Clean text snippet:", clean[:1000])
except Exception as e:
    print("Err:", e)

