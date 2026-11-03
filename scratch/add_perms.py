with open('backend/app/routers/admin_ops.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    if 'stats_perm = require("statistics")' in line:
        new_lines.append('marketing_perm = require("marketing")\n')
        new_lines.append('catalog_perm = require("products")\n')

with open('backend/app/routers/admin_ops.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Perms inserted successfully!")

