with open(r"frontend\src\miniapp\MiniApp.tsx", "r", encoding="utf-8") as f:
    text = f.read()

bad = "toast(\"Ulashish oynasi ochildi!\", \"success\");\n  };\n    shopFetch(\"/api/shop/orders\")"
good = "toast(\"Ulashish oynasi ochildi!\", \"success\");\n  };\n\n  useEffect(() => {\n    shopFetch(\"/api/shop/orders\")"

text = text.replace(bad, good)
text = text.replace(bad.replace("\n", "\r\n"), good.replace("\n", "\r\n"))

with open(r"frontend\src\miniapp\MiniApp.tsx", "w", encoding="utf-8") as f:
    f.write(text)

print("Replacement done!")
