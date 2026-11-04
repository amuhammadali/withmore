from bs4 import BeautifulSoup
import re
import json

with open(r"c:\Users\muham\OneDrive\Desktop\withmore\scratch\oneuz_magicbot_home.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

print("=== HEADER / NAVBAR ===")
header = soup.find("header")
if header:
    print("Header classes:", header.get("class"))
    for el in header.find_all(['a', 'button', 'input']):
        print("Header element:", el.name, el.get("class"), el.get_text(strip=True)[:40])

print("\n=== HERO / BANNER ===")
# Look for banner or hero images
banners = soup.find_all("img")
for img in banners[:8]:
    print("Img src:", img.get("src")[:80], "alt:", img.get("alt"))

print("\n=== CATEGORIES / TABS ===")
# Look for category chips or slider
cat_containers = soup.find_all(lambda t: t.name in ['div', 'nav', 'ul'] and any('categor' in c.lower() for c in t.get('class', [])))
for cc in cat_containers[:3]:
    print("Cat container:", cc.get("class"))
    print(cc.get_text(separator=' | ', strip=True)[:150])

print("\n=== PRODUCT CARD STRUCTURE ===")
# Find product links or cards
prod_links = soup.find_all('a', href=re.compile(r'/products/'))
if prod_links:
    first_card = prod_links[0]
    print("Card parent classes:", first_card.parent.get("class"))
    print("Card HTML snippet:\n", str(first_card)[:800])

print("\n=== BOTTOM NAVIGATION BAR ===")
# Look for bottom nav / tabbar
bottom_navs = soup.find_all(lambda t: t.name in ['nav', 'footer', 'div'] and any('bottom' in c.lower() or 'tabbar' in c.lower() or 'fixed' in c.lower() for c in t.get('class', [])))
for bn in bottom_navs[:3]:
    print("Bottom nav class:", bn.get("class"))
    print("Text:", bn.get_text(separator=' | ', strip=True)[:150])

