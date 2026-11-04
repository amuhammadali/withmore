import re

file_path = r"frontend/src/miniapp/MiniApp.tsx"

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# ----------------- 1. HOME SCREEN: Add Search & Filter Tabs -----------------
# Target the category section
cat_section_target = """      {/* Editorial Luxury Category Chips Row (Lookbook now in categories!) */}
      <section
        aria-label="Kategoriyalar"
        className="px-4 py-4"
      >"""

search_and_filters = """      {/* Search Bar & Quick Filter Tabs (ONE23 Style) */}
      <section className="px-4 pt-3.5 space-y-2.5">
        <div className="relative flex items-center rounded-2xl border border-slate-200/90 bg-white shadow-xs focus-within:border-[#c5a676] focus-within:ring-2 focus-within:ring-[#c5a676]/20 transition">
          <span className="pl-3.5 text-slate-400">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
          </span>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={lang === "ru" ? "Поиск товаров (костюм, рубашка, лоферы...)" : "Tovarlarni qidirish (kostyum, ko'ylak, loufer...)"}
            className="w-full bg-transparent px-3 py-2.5 text-xs text-slate-900 placeholder:text-slate-400 outline-none"
          />
          {searchQuery && (
            <button type="button" onClick={() => setSearchQuery("")} className="pr-3 text-xs text-slate-400 hover:text-slate-700 cursor-pointer">✕</button>
          )}
        </div>

        {/* Quick Filter Pills */}
        <div className="flex gap-1.5 overflow-x-auto no-scrollbar pb-0.5">
          {[
            { key: "all", label_uz: "Barchasi", label_ru: "Все", icon: "" },
            { key: "new", label_uz: "Yangi kelganlar", label_ru: "Новинки", icon: "⚡" },
            { key: "bestseller", label_uz: "Xaridorgir", label_ru: "Хиты", icon: "🔥" },
            { key: "sale", label_uz: "Chegirmalar", label_ru: "Скидки", icon: "🏷️" },
          ].map((f) => (
            <button
              key={f.key}
              type="button"
              onClick={() => {
                setQuickFilter(f.key as any);
                if (selectedCatId === "lookbook") setSelectedCatId(null);
              }}
              className={`shrink-0 flex items-center gap-1 rounded-full px-3 py-1.5 text-[10.5px] font-bold transition cursor-pointer ${
                quickFilter === f.key && selectedCatId !== "lookbook"
                  ? "bg-[#172641] text-[#f5f1e8] shadow-xs"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {f.icon && <span>{f.icon}</span>}
              <span>{lang === "ru" ? f.label_ru : f.label_uz}</span>
            </button>
          ))}
        </div>
      </section>

      {/* Editorial Luxury Category Chips Row (Lookbook now in categories!) */}
      <section
        aria-label="Kategoriyalar"
        className="px-4 py-3"
      >"""

if cat_section_target in text and "Search Bar & Quick Filter Tabs" not in text:
    text = text.replace(cat_section_target, search_and_filters, 1)
    print("Added Search & Quick Filters to HomeScreen!")

# Update activeProds logic in HomeScreen
old_active_prods = """              const activeProds = selectedCatId === null
                ? (featured.length > 0 ? featured : allProds).slice(0, 8)
                : allProds.filter(p => p.category_id === selectedCatId);"""

new_active_prods = """              let activeProds = selectedCatId === null
                ? (featured.length > 0 ? featured : allProds)
                : allProds.filter(p => p.category_id === selectedCatId);

              if (searchQuery.trim()) {
                const q = searchQuery.toLowerCase().trim();
                activeProds = allProds.filter((p: any) =>
                  (p.name_uz && p.name_uz.toLowerCase().includes(q)) ||
                  (p.name_ru && p.name_ru.toLowerCase().includes(q)) ||
                  (p.material && p.material.toLowerCase().includes(q))
                );
              } else if (quickFilter === "new") {
                activeProds = [...allProds].sort((a: any, b: any) => b.id - a.id);
              } else if (quickFilter === "bestseller") {
                activeProds = allProds.filter((p: any) => p.featured || (p.stock_total && p.stock_total > 4));
                if (activeProds.length === 0) activeProds = allProds.slice(0, 6);
              } else if (quickFilter === "sale") {
                activeProds = allProds.filter((p: any) => p.sale_type === "stock" || p.price < 900000);
              }

              activeProds = activeProds.slice(0, 12);"""

if old_active_prods in text:
    text = text.replace(old_active_prods, new_active_prods, 1)
    print("Updated activeProds filtering in HomeScreen!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("HomeScreen updates complete!")

