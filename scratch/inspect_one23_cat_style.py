from bs4 import BeautifulSoup
import re

with open(r"c:\Users\muham\OneDrive\Desktop\withmore\scratch\oneuz_magicbot_home.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# Find the section containing "Ustki kiyim"
for a in soup.find_all('a', href=re.compile(r'/categories/')):
    print("Cat link tag:", a.prettify()[:600])
    break

