import re

file_path = r"frontend/src/miniapp/MiniApp.tsx"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# Helper function definition to insert above HomeScreen or near getCategoryIcon
cat_visual_func = """
// ---------------- CIRCULAR CATEGORY STORY ICONS ----------------
function getCategoryCircleVisual(id: number | "lookbook" | "all", name: string) {
  if (id === "all") {
    return (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9">
        <rect x="3" y="3" width="7" height="7" rx="1.5" />
        <rect x="14" y="3" width="7" height="7" rx="1.5" />
        <rect x="14" y="14" width="7" height="7" rx="1.5" />
        <rect x="3" y="14" width="7" height="7" rx="1.5" />
      </svg>
    );
  }
  if (id === "lookbook") {
    return (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M6 3l6 9 6-9v17H6V3z" />
        <path d="M12 12v9" />
        <path d="M8 3h8" />
      </svg>
    );
  }
  const n = (name || "").toLowerCase();
  if (n.includes("kostyum") || n.includes("kastyum") || n.includes("smoking")) {
    return (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M4 4l5 2 3-3 3 3 5-2v15l-8 3-8-3V4z" />
        <path d="M12 3v18" />
      </svg>
    );
  }
  if (n.includes("ko'ylak") || n.includes("koylak") || n.includes("futbolka") || n.includes("rubashka")) {
    return (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M8 3h8l4 4-2 3-3-2v13H9V8L7 10 5 7l3-4z" />
        <path d="M12 3v18" />
      </svg>
    );
  }
  if (n.includes("shim") || n.includes("jinsi") || n.includes("bryuk")) {
    return (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M4 4h16l-2 17-5-1-1-9-1 9-5 1L4 4z" />
      </svg>
    );
  }
  if (n.includes("oyoq") || n.includes("poyabzal") || n.includes("tufli") || n.includes("loufer")) {
    return (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M3 13h12a4 4 0 0 1 4 4v2H3v-6z" />
        <path d="M15 13l-4-6H5v6" />
      </svg>
    );
  }
  if (n.includes("aksessuar") || n.includes("kamar") || n.includes("galstuk")) {
    return (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <circle cx="12" cy="12" r="7" />
        <polyline points="12 9 12 12 14 14" />
        <path d="M12 5V2" />
        <path d="M12 22v-3" />
      </svg>
    );
  }
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" />
      <line x1="7" y1="7" x2="7.01" y2="7" />
    </svg>
  );
}
"""

if "function getCategoryCircleVisual" not in code:
    # Insert right before function HomeScreen
    code = code.replace("function HomeScreen({", cat_visual_func + "\nfunction HomeScreen({", 1)
    print("Added getCategoryCircleVisual function!")

# Now replace the Search & Quick Filter and Category row in HomeScreen
old_cat_section_regex = r"\{\/\* Search Bar & Quick Filter Tabs.*?\{\/\* Main Content Area based on Selected Category \*\/\}"

new_cat_section = """{/* Search Bar (ONE23 Style) */}
      <section className="px-4 pt-3.5">
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
      </section>

      {/* Stories-Style Circular Categories Bar (Dumaloq Toifalar) */}
      <section
        aria-label="Kategoriyalar"
        className="px-4 pt-3.5 pb-2"
      >
        <div className="flex items-center justify-between mb-2">
          <span className="text-[10px] font-bold uppercase tracking-[.2em] text-[#8a6c43]">
            {lang === "ru" ? "Категории" : "Kolleksiyalar"}
          </span>
          <Link
            to="/miniapp/catalog"
            className="text-[11px] font-semibold text-slate-900 hover:underline"
          >
            {lang === "ru" ? "Все →" : "Barchasi →"}
          </Link>
        </div>

        <div className="flex gap-3 overflow-x-auto no-scrollbar pb-1 pt-0.5">
          {/* Barchasi Bubble */}
          <button
            type="button"
            onClick={() => {
              setSelectedCatId(null);
            }}
            className="flex flex-col items-center gap-1.5 shrink-0 cursor-pointer group active:scale-95 transition-transform"
          >
            <div className={`relative flex items-center justify-center w-15 h-15 rounded-full transition-all duration-300 ${
              selectedCatId === null
                ? "bg-[#172641] text-white ring-2.5 ring-[#172641] ring-offset-2 ring-offset-white shadow-md scale-105"
                : "bg-white text-slate-700 border border-slate-200/90 shadow-2xs hover:border-[#172641]/40 group-hover:scale-102"
            }`}>
              {getCategoryCircleVisual("all", "Barchasi")}
            </div>
            <span className={`text-[11px] max-w-[68px] truncate text-center leading-tight transition-colors ${
              selectedCatId === null ? "font-bold text-[#172641]" : "font-medium text-slate-600 group-hover:text-slate-900"
            }`}>
              {t.allCategories}
            </span>
          </button>

          {/* Tayyor Obrazlar (Lookbook) Bubble */}
          <button
            type="button"
            onClick={() => {
              setSelectedCatId("lookbook");
            }}
            className="flex flex-col items-center gap-1.5 shrink-0 cursor-pointer group active:scale-95 transition-transform"
          >
            <div className={`relative flex items-center justify-center w-15 h-15 rounded-full transition-all duration-300 ${
              selectedCatId === "lookbook"
                ? "bg-gradient-to-br from-[#172641] to-[#25395b] text-[#f5f1e8] ring-2.5 ring-[#c5a676] ring-offset-2 ring-offset-white shadow-md scale-105"
                : "bg-white text-slate-700 border border-[#c5a676]/60 shadow-2xs hover:border-[#c5a676] group-hover:scale-102"
            }`}>
              {getCategoryCircleVisual("lookbook", "Obrazlar")}
              <span className="absolute -top-1 -right-1 rounded-full bg-[#c5a676] px-1.5 py-0.2 text-[8px] font-black text-slate-950 shadow-xs border border-white">
                -10%
              </span>
            </div>
            <span className={`text-[11px] max-w-[68px] truncate text-center leading-tight transition-colors ${
              selectedCatId === "lookbook" ? "font-bold text-[#172641]" : "font-medium text-slate-600 group-hover:text-slate-900"
            }`}>
              {lang === "ru" ? "Образы" : "Obrazlar"}
            </span>
          </button>

          {/* Dynamic Categories Bubbles */}
          {categories.map((c) => {
            const label = lang === "ru" ? c.name_ru || c.name_uz : c.name_uz;
            const active = selectedCatId === c.id;
            return (
              <button
                key={c.id}
                type="button"
                onClick={() => {
                  setSelectedCatId(c.id);
                }}
                className="flex flex-col items-center gap-1.5 shrink-0 cursor-pointer group active:scale-95 transition-transform"
              >
                <div className={`relative flex items-center justify-center w-15 h-15 rounded-full transition-all duration-300 ${
                  active
                    ? "bg-[#172641] text-white ring-2.5 ring-[#172641] ring-offset-2 ring-offset-white shadow-md scale-105"
                    : "bg-white text-slate-700 border border-slate-200/90 shadow-2xs hover:border-[#172641]/40 group-hover:scale-102"
                }`}>
                  {getCategoryCircleVisual(c.id, c.name_uz)}
                </div>
                <span className={`text-[11px] max-w-[68px] truncate text-center leading-tight transition-colors ${
                  active ? "font-bold text-[#172641]" : "font-medium text-slate-600 group-hover:text-slate-900"
                }`}>
                  {label}
                </span>
              </button>
            );
          })}
        </div>
      </section>

      {/* Main Content Area based on Selected Category */}"""

match = re.search(old_cat_section_regex, code, re.DOTALL)
if match:
    code = code[:match.start()] + new_cat_section + code[match.end():]
    print("Replaced category section with Stories-Style Circular Categories!")
else:
    print("Could not match old category section regex.")

# Now update the section header above regular products grid to include Quick Filter pills
old_regular_heading = """        /* REGULAR PRODUCTS GRID VIEW */
        <section className="px-4 pt-2 rise-in">
          <div className="mb-4 flex items-end justify-between border-b border-slate-200/80 pb-2.5">
            <div>
              <h2 className="font-display text-[24px] font-medium text-slate-900">
                {t.curatedModels}
              </h2>
              <span className="text-[10px] font-bold uppercase tracking-[.16em] text-[#8a6c43] block mt-0.5">
                {t.curatedSubtitle}
              </span>
            </div>
            <Link
              to="/miniapp/catalog"
              className="text-[10px] font-bold uppercase tracking-[.16em] text-[#8a6c43] no-underline hover:underline"
            >
              {t.viewAll} · {allProds.length}
            </Link>
          </div>"""

new_regular_heading = """        /* REGULAR PRODUCTS GRID VIEW */
        <section className="px-4 pt-2 rise-in">
          <div className="mb-3.5 flex flex-wrap items-center justify-between gap-2 border-b border-slate-200/80 pb-2.5">
            <div>
              <h2 className="font-display text-[20px] font-semibold text-slate-900">
                {selectedCatId === null
                  ? (lang === "ru" ? "Все товары" : "Tanlangan modellar")
                  : (categories.find(c => c.id === selectedCatId)?.name_uz || "Kolleksiya")}
              </h2>
            </div>

            {/* ONE23 Quick Filter Pills (Without redundant Barchasi) */}
            <div className="flex items-center gap-1.5">
              {[
                { key: "new", label_uz: "Yangi", label_ru: "Новинки", icon: "⚡" },
                { key: "bestseller", label_uz: "Xit", label_ru: "Хиты", icon: "🔥" },
                { key: "sale", label_uz: "Chegirma", label_ru: "Скидки", icon: "🏷️" },
              ].map((f) => {
                const active = quickFilter === f.key;
                return (
                  <button
                    key={f.key}
                    type="button"
                    onClick={() => setQuickFilter(active ? "all" : (f.key as any))}
                    className={`flex items-center gap-1 rounded-full px-2.5 py-1 text-[10px] font-bold transition cursor-pointer ${
                      active
                        ? "bg-[#172641] text-white shadow-2xs"
                        : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                    }`}
                  >
                    <span>{f.icon}</span>
                    <span>{lang === "ru" ? f.label_ru : f.label_uz}</span>
                  </button>
                );
              })}
            </div>
          </div>"""

if old_regular_heading in code:
    code = code.replace(old_regular_heading, new_regular_heading, 1)
    print("Updated regular products heading with quick filter chips!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Finished Circular Category design script!")

