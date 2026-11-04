import re
from bs4 import BeautifulSoup

with open(r"c:\Users\muham\OneDrive\Desktop\withmore\scratch\oneuz_magicbot_home.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# 1. Navigation & Links
nav_links = []
for a in soup.find_all("a", href=True):
    href = a.get("href", "")
    text = a.get_text(strip=True)
    if text and href and len(text) < 50:
        nav_links.append((text, href))

# Remove duplicates while preserving order
seen = set()
unique_links = []
for text, href in nav_links:
    if (text, href) not in seen:
        seen.add((text, href))
        unique_links.append((text, href))

print("=== NAVIGATION LINKS ===")
for text, href in unique_links[:40]:
    print(f"- {text} -> {href}")

# 2. Look at Malika / AI assistant / Chat
chat_divs = soup.find_all(lambda tag: tag.name in ['div', 'button', 'span', 'section'] and any(k in str(tag).lower() for k in ['malika', 'ai-chat', 'assistant', 'chat-widget']))
print("\n=== AI ASSISTANT / CHAT SNIPPETS ===")
for d in chat_divs[:5]:
    txt = d.get_text(separator=' ', strip=True)
    if len(txt) > 20 and len(txt) < 300:
        print("Chat widget text:", txt)

