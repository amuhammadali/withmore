from bs4 import BeautifulSoup
import re

with open(r"c:\Users\muham\OneDrive\Desktop\withmore\scratch\oneuz_magicbot_home.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

for nav in soup.find_all(['nav', 'footer', 'div']):
    c = ' '.join(nav.get('class', []))
    if 'fixed' in c and 'bottom' in c:
        print("Found fixed bottom element:", c)
        print(nav.prettify()[:1000])
        break
else:
    # Look for tabbar or mobile navigation
    for el in soup.find_all(attrs={"class": re.compile(r'(tabbar|mobile-nav|bottom-bar)', re.I)}):
        print("Found class match:", el.get('class'))

