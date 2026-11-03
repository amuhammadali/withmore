with open(r"frontend\src\miniapp\MiniApp.tsx", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if "// Sartorial Measurements Profile" in line:
        skip = True
    elif skip and "shopFetch(\"/api/shop/orders\")" in line:
        skip = False
        new_lines.append(line)
        continue
    
    if not skip:
        new_lines.append(line)

with open(r"frontend\src\miniapp\MiniApp.tsx", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Finished cleaning. New line count:", len(new_lines))
