from bs4 import BeautifulSoup
import re

with open(r"c:\Users\muham\OneDrive\Desktop\withmore\scratch\oneuz_magicbot_home.html", "r", encoding="utf-8") as f:
    html = f.read()

# Find scripts, title, buttons, nav, categories
title = re.findall(r'<title>(.*?)</title>', html)
print("Title:", title)

# Look for categories
categories = re.findall(r'href="([^"]*(?:category|catalog|collection)[^"]*)"', html, re.I)
print("Category links:", set(categories[:15]))

# Look for navigation links or headings
headings = re.findall(r'<h[1-4][^>]*>(.*?)</h[1-4]>', html, re.I)
print("Headings:", [re.sub(r'<[^>]+>', '', h).strip() for h in headings[:15]])

# Look for chat/AI widgets
chat_matches = re.findall(r'(malika|chat|assistant|bot|consultant|ai)', html, re.I)
print("Chat keywords count:", len(chat_matches))

# Look for payment methods
payments = re.findall(r'(payme|click|uzum|humo|uzcard|cash)', html, re.I)
print("Payment mentions:", set([p.lower() for p in payments]))

# Look for script sources
scripts = re.findall(r'<script[^>]+src="([^"]+)"', html)
print("External scripts:", scripts[:10])

