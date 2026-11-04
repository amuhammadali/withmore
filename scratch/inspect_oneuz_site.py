import urllib.request
import json
import re

base_url = "https://oneuz.magicbot.store"
req = urllib.request.Request(base_url, headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'})

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print("HTML length:", len(html))
        
        # Save html to scratch for inspection
        with open(r"c:\Users\muham\OneDrive\Desktop\withmore\scratch\oneuz_magicbot_home.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        # Look for scripts, api endpoints, state
        api_endpoints = re.findall(r'["\'](/api/[^"\']+)["\']', html)
        print("API endpoints found:", set(api_endpoints))
        
        # Look for JSON state (Next.js, Nuxt, Redux, or window data)
        next_data = re.findall(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html)
        if next_data:
            print("Next.js app detected! Length:", len(next_data[0]))
            with open(r"c:\Users\muham\OneDrive\Desktop\withmore\scratch\oneuz_next_data.json", "w", encoding="utf-8") as f:
                f.write(next_data[0])
        else:
            print("Not Next.js or different state.")
            
except Exception as e:
    print("Error:", e)

