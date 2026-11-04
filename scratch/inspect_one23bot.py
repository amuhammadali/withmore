import urllib.request
import re

url = 'https://t.me/One23uzbot'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print("HTML length:", len(html))
        titles = re.findall(r'<title>(.*?)</title>', html)
        descriptions = re.findall(r'<meta property="og:description" content="(.*?)"', html)
        images = re.findall(r'<meta property="og:image" content="(.*?)"', html)
        extra = re.findall(r'<div class="tgme_page_description.*?>(.*?)</div>', html, re.DOTALL)
        
        print("Title:", titles)
        print("Desc:", descriptions)
        print("Image:", images)
        if extra:
            print("Page desc:", extra[0].strip())
except Exception as e:
    print("Err:", e)

