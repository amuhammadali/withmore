with open(r'backend\app\routers\shop.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    '"sizes": [v.size for v in prod.variants if v.available],',
    '"sizes": [v.size for v in prod.variants if v.size and (prod.sale_type == "preorder" or (v.stock or 0) > 0)],'
)

text = text.replace(
    'first_avail = next((v for v in prod.variants if v.available), prod.variants[0])',
    'first_avail = next((v for v in prod.variants if prod.sale_type == "preorder" or (v.stock or 0) > 0), prod.variants[0])'
)

with open(r'backend\app\routers\shop.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed shop.py variants successfully!")

