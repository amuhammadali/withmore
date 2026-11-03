import re

# 1. Update frontend/src/admin/AdminApp.tsx
with open(r'frontend\src\admin\AdminApp.tsx', 'r', encoding='utf-8') as f:
    admin_app = f.read()

# Add /admin/broadcast to NAV_ITEMS right after CRM
old_crm_block = '''  {
    to: "/admin/crm",
    labelUz: "📊 CRM Voronka",
    labelRu: "📊 CRM Воронка",
    subUz: "Pipeline & Razmerlar",
    subRu: "Сделки и задачи",
    perm: "orders",
    icon: "M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2",
  },'''

new_crm_and_broadcast = '''  {
    to: "/admin/crm",
    labelUz: "📊 CRM Voronka",
    labelRu: "📊 CRM Воронка",
    subUz: "Pipeline & Razmerlar",
    subRu: "Сделки и задачи",
    perm: "orders",
    icon: "M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2",
  },
  {
    to: "/admin/broadcast",
    labelUz: "📢 Telegram Broadcast",
    labelRu: "📢 Рассылка клиентам",
    subUz: "Xabarnoma yuborish",
    subRu: "Telegram рассылка",
    perm: "orders",
    icon: "M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z",
  },'''

if old_crm_block in admin_app:
    admin_app = admin_app.replace(old_crm_block, new_crm_and_broadcast)
    print("Added Telegram Broadcast to sidebar NAV_ITEMS successfully!")
else:
    print("Could not find old_crm_block!")

# Add broadcast route
old_route_marketing = '''            <Route
              path="marketing"
              element={
                can("statistics") ? <MarketingPage /> : <PermissionDenied />
              }
            />'''

new_route_marketing = '''            <Route
              path="broadcast"
              element={<MarketingPage />}
            />
            <Route
              path="marketing"
              element={<MarketingPage />}
            />'''

if old_route_marketing in admin_app:
    admin_app = admin_app.replace(old_route_marketing, new_route_marketing)
    print("Added /admin/broadcast and /admin/marketing routes successfully!")
else:
    print("Could not find old_route_marketing!")

with open(r'frontend\src\admin\AdminApp.tsx', 'w', encoding='utf-8') as f:
    f.write(admin_app)

print("AdminApp.tsx updated successfully!")

