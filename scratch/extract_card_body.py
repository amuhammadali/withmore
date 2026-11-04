from bs4 import BeautifulSoup
import re

with open(r"c:\Users\muham\OneDrive\Desktop\withmore\scratch\oneuz_magicbot_home.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

prod = soup.find('a', href=re.compile(r'/products/'))
if prod:
    card = prod.parent
    while card and ('grid' not in ' '.join(card.get('class', [])) and card.name != 'body'):
        prev = card
        card = card.parent
        if 'grid' in ' '.join(card.get('class', [])):
            card = prev
            break
    print("=== CARD TEXT AND BUTTONS ===")
    print(card.prettify()[-1200:])

