from bs4 import BeautifulSoup
import re

with open(r"c:\Users\muham\OneDrive\Desktop\withmore\scratch\oneuz_magicbot_home.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

for nav in soup.find_all('nav'):
    print("Nav classes:", nav.get('class'))
    print("Nav text:", nav.get_text(separator=' | ', strip=True)[:200])

# Look for links with icons
for a in soup.find_all('a'):
    txt = a.get_text(strip=True)
    if txt in ['Главная', 'Каталог', 'Корзина', 'Избранное', 'Профиль', 'Bosh sahifa', 'Katalog', 'Savat', 'Sevimlilar', 'Profil']:
        print("Tab item found:", txt, a.get('href'), a.parent.get('class'))

