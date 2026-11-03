with open('backend/app/routers/admin_ops.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Add permissions
target = 'stats_perm = require("statistics")'
replacement = 'stats_perm = require("statistics")\nmarketing_perm = require("marketing")\ncatalog_perm = require("products")'

if target in text and 'marketing_perm' not in text:
    text = text.replace(target, replacement)

# Add imports
imp_target = 'from ..models import STATUS_UZ, STATUSES, AdminAccount, Order, Product, now'
imp_replacement = 'from ..models import STATUS_UZ, STATUSES, AdminAccount, Order, Product, Customer, ShopSession, LookbookBundle, BroadcastCampaign, now\nfrom ..notifications import enqueue'

if imp_target in text:
    text = text.replace(imp_target, imp_replacement)

with open('backend/app/routers/admin_ops.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Fixed imports in admin_ops.py!')

