import re

file_path = r"frontend/src/miniapp/MiniApp.tsx"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update HomeScreen with Search and Filter tabs
# Look for: const [selectedCatId, setSelectedCatId] = useState<number | "lookbook" | null>(null);
old_home_state = '  const [selectedCatId, setSelectedCatId] = useState<number | "lookbook" | null>(null);'
new_home_state = '''  const [selectedCatId, setSelectedCatId] = useState<number | "lookbook" | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [quickFilter, setQuickFilter] = useState<"all" | "new" | "bestseller" | "sale">("all");'''

if old_home_state in content and 'const [searchQuery' not in content:
    content = content.replace(old_home_state, new_home_state, 1)
    print("HomeScreen state updated!")

# 2. Update ProductScreen to include activeTab state
old_prod_state = '  const [quickLoading, setQuickLoading] = useState(false);'
new_prod_state = '''  const [quickLoading, setQuickLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"desc" | "reviews" | "delivery">("desc");'''

if old_prod_state in content and 'const [activeTab' not in content:
    content = content.replace(old_prod_state, new_prod_state, 1)
    print("ProductScreen state updated!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Initial hook updates done!")
