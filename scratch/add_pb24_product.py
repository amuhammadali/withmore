with open(r"frontend/src/miniapp/MiniApp.tsx", "r", encoding="utf-8") as f:
    text = f.read()

target = '<div className="rise-in">\n      {/* ONE23 Breadcrumbs */}'
repl = '<div className="rise-in pb-24">\n      {/* ONE23 Breadcrumbs */}'

text = text.replace(target, repl)
text = text.replace(target.replace("\n", "\r\n"), repl.replace("\n", "\r\n"))

with open(r"frontend/src/miniapp/MiniApp.tsx", "w", encoding="utf-8") as f:
    f.write(text)

print("Added pb-24 to ProductScreen!")

