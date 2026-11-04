from bs4 import BeautifulSoup

with open(r"c:\Users\muham\OneDrive\Desktop\withmore\scratch\oneuz_magicbot_home.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
header = soup.find("header")
if header:
    print(header.prettify()[:1500])

