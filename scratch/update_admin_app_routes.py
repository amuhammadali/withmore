with open(r'frontend\src\admin\AdminApp.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace import
text = text.replace('MarketingPage,', 'BroadcastPage,\n  MarketingPage,')

# Replace broadcast route
text = text.replace(
    'path="broadcast"\n              element={<MarketingPage />}',
    'path="broadcast"\n              element={<BroadcastPage />}'
)

# Update sidebar label for marketing to be distinct
old_marketing_item = '''  {
    to: "/admin/marketing",
    labelUz: "Marketing",
    labelRu: "Маркетинг",
    subUz: "Manbalar",
    subRu: "Источники",
    perm: "statistics",
    icon: "M18 20V10M12 20V4M6 20v-6",
  },'''

new_marketing_item = '''  {
    to: "/admin/marketing",
    labelUz: "📈 Reklama & UTM",
    labelRu: "📈 Реклама и UTM",
    subUz: "Trafik tahlili",
    subRu: "Анализ источников",
    perm: "statistics",
    icon: "M18 20V10M12 20V4M6 20v-6",
  },'''

if old_marketing_item in text:
    text = text.replace(old_marketing_item, new_marketing_item)

with open(r'frontend\src\admin\AdminApp.tsx', 'w', encoding='utf-8') as f:
    f.write(text)

print("AdminApp.tsx routes and labels updated successfully!")

