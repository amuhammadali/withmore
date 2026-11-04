from bs4 import BeautifulSoup
import re

with open(r"c:\Users\muham\OneDrive\Desktop\withmore\scratch\oneuz_magicbot_home.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# Find product card container (look around product link)
prod = soup.find('a', href=re.compile(r'/products/'))
if prod:
    # Go up 2 or 3 parents to get the whole card
    card = prod.parent
    while card and ('grid' not in ' '.join(card.get('class', [])) and card.name != 'body'):
        prev = card
        card = card.parent
        if 'grid' in ' '.join(card.get('class', [])):
            card = prev
            break
    print("=== FULL PRODUCT CARD ===")
    print(card.prettify()[:1500])

# Find the bottom fixed tab bar
print("\n=== FIXED BOTTOM TAB BAR ===")
for nav in soup.find_all(['nav', 'div']):
    classes = ' '.join(nav.get('class', []))
    if 'fixed' in classes and 'bottom-0' in classes:
        print("Classes:", classes)
        print(nav.prettify()[:1000])
        break

