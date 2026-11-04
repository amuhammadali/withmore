import urllib.request
import re

url = "https://one23.magicbot.store"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for target_url in [
    "https://one23.magicbot.store",
    "https://magicbot.store/store/one23",
    "https://magicstore.uz/one23",
]:
    try:
        req = urllib.request.Request(target_url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            print(f"SUCCESS: {target_url} - Len: {len(content)}")
            # print title and meta
            title = re.findall(r'<title>(.*?)</title>', content)
            print("Title:", title)
            # find keywords or navigation
            links = re.findall(r'href="([^"]+)"', content)
            print("Found links count:", len(links))
            print("Sample links:", links[:10])
            break
    except Exception as e:
        print(f"Failed {target_url}: {e}")

