from bs4 import BeautifulSoup

with open(r"c:\Users\muham\OneDrive\Desktop\withmore\scratch\oneuz_magicbot_home.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

main = soup.find("main")
if main:
    for i, child in enumerate(main.children):
        if child.name:
            print(f"Child {i}: <{child.name} class='{' '.join(child.get('class', []))}'>")
            print(child.get_text(separator=' ', strip=True)[:100])

