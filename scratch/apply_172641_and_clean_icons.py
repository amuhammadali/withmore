import os

file_path = r"c:\Users\muham\OneDrive\Desktop\withmore\frontend\src\miniapp\MiniApp.tsx"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update BrandMarquee in MiniApp.tsx to use #172641 luxury ribbon
old_marquee_start = "// ---------------- LUXURY BRAND LOGO MARQUEE TICKER ----------------"
old_marquee_end = "// ---------------- HOME SCREEN (REPLIT EDITORIAL) ----------------"

start_idx = content.find(old_marquee_start)
end_idx = content.find(old_marquee_end)

if start_idx != -1 and end_idx != -1:
    new_marquee = """// ---------------- LUXURY BRAND LOGO MARQUEE TICKER ----------------
function BrandMarquee() {
  const marqueeItems = [...BRAND_LOGOS, ...BRAND_LOGOS];

  return (
    <section
      aria-label="Original brendlar va mato uylari"
      className="relative overflow-hidden border-y border-[#c5a676]/30 bg-[#172641] py-3.5 text-white shadow-sm"
    >
      {/* Edge gradient mask for smooth fade in/out */}
      <div className="pointer-events-none absolute inset-y-0 left-0 w-12 sm:w-20 bg-gradient-to-r from-[#172641] to-transparent z-10" />
      <div className="pointer-events-none absolute inset-y-0 right-0 w-12 sm:w-20 bg-gradient-to-l from-[#172641] to-transparent z-10" />

      <div className="animate-marquee flex items-center gap-3 sm:gap-5">
        {marqueeItems.map((b, idx) => (
          <div
            key={idx}
            className="group flex items-center gap-3 shrink-0 rounded-2xl border border-white/10 bg-white/[0.06] px-4 py-2 backdrop-blur-md transition-all duration-300 hover:border-[#c5a676]/70 hover:bg-white/[0.12] hover:scale-105 shadow-xs"
          >
            <div className="text-white group-hover:text-[#f4efe5] transition-colors">
              {b.svg}
            </div>
            <div className="h-5 w-px bg-white/20" />
            <div className="text-left">
              <div className="text-[9px] font-bold uppercase tracking-[.18em] text-[#c5a676]">
                {b.origin}
              </div>
              <div className="text-[7.5px] font-semibold text-white/75 tracking-wider uppercase whitespace-nowrap">
                {b.type}
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

"""
    content = content[:start_idx] + new_marquee + content[end_idx:]
    print("BrandMarquee updated with #172641!")

# 2. Update Highlights in HomeScreen: Remove emoji icons
old_highlights = """      {/* Atelier Excellence Highlights */}
      <section className="mx-4 mt-4 mb-2 rounded-2xl border border-slate-200/80 bg-white p-3.5 shadow-[0_2px_8px_rgba(0,0,0,0.03)]">
        <div className="grid grid-cols-3 gap-2 text-center divide-x divide-slate-100">
          <div className="px-1">
            <div className="text-base mb-1">✂️</div>
            <div className="text-[11px] font-bold text-slate-900">Aniq Bichim</div>
            <div className="text-[9px] font-medium text-slate-400 mt-0.5">Qaddi-qomatga mos</div>
          </div>
          <div className="px-1">
            <div className="text-base mb-1">🇮🇹</div>
            <div className="text-[11px] font-bold text-slate-900">100% Original</div>
            <div className="text-[9px] font-medium text-slate-400 mt-0.5">Italiya & Angliya</div>
          </div>
          <div className="px-1">
            <div className="text-base mb-1">⚡</div>
            <div className="text-[11px] font-bold text-slate-900">Tezkor Kuryer</div>
            <div className="text-[9px] font-medium text-slate-400 mt-0.5">Butun O‘zbekiston</div>
          </div>
        </div>
      </section>"""

new_highlights = """      {/* Atelier Excellence Highlights */}
      <section className="mx-4 mt-4 mb-2 rounded-2xl border border-slate-200/80 bg-white py-3.5 px-3 shadow-[0_2px_8px_rgba(0,0,0,0.03)]">
        <div className="grid grid-cols-3 gap-1 text-center divide-x divide-slate-100">
          <div className="px-1">
            <div className="text-[11px] font-bold tracking-tight text-[#172641]">Aniq Bichim</div>
            <div className="text-[9px] font-medium text-slate-400 mt-0.5">Qaddi-qomatga mos</div>
          </div>
          <div className="px-1">
            <div className="text-[11px] font-bold tracking-tight text-[#172641]">100% Original</div>
            <div className="text-[9px] font-medium text-slate-400 mt-0.5">Italiya & Angliya</div>
          </div>
          <div className="px-1">
            <div className="text-[11px] font-bold tracking-tight text-[#172641]">Tezkor Kuryer</div>
            <div className="text-[9px] font-medium text-slate-400 mt-0.5">Butun O‘zbekiston</div>
          </div>
        </div>
      </section>"""
content = content.replace(old_highlights, new_highlights)

# 3. Remove icons from HomeScreen categories
old_home_categories = """          <div className="flex gap-2.5 overflow-x-auto no-scrollbar pb-1">
            <Link
              to="/miniapp/catalog"
              className="shrink-0 flex items-center gap-2 rounded-2xl bg-slate-900 px-4 py-2.5 text-[11px] font-bold text-white shadow-sm ring-1 ring-slate-900 no-underline transition-all duration-200 hover:scale-[1.02] active:scale-95"
            >
              <span className="text-sm drop-shadow-sm">✨</span>
              <span className="tracking-wide">{t.allCategories}</span>
            </Link>
            {categories.map((c) => {
              const label = lang === "ru" ? c.name_ru || c.name_uz : c.name_uz;
              const icon = getCategoryIcon(label);
              return (
                <Link
                  key={c.id}
                  to={`/miniapp/catalog?category=${c.id}`}
                  className="shrink-0 flex items-center gap-2 rounded-2xl border border-slate-200/90 bg-white px-4 py-2.5 text-[11px] font-bold text-slate-800 shadow-[0_1px_4px_rgba(0,0,0,0.03)] no-underline transition-all duration-200 hover:border-slate-300 hover:shadow-md hover:-translate-y-0.5 hover:text-black active:scale-95"
                >
                  <span className="text-sm">{icon}</span>
                  <span className="tracking-wide">{label}</span>
                </Link>
              );
            })}
          </div>"""

new_home_categories = """          <div className="flex gap-2 overflow-x-auto no-scrollbar pb-1">
            <Link
              to="/miniapp/catalog"
              className="shrink-0 flex items-center rounded-2xl bg-[#172641] px-4 py-2.5 text-[11.5px] font-bold text-white shadow-sm ring-1 ring-[#172641] no-underline transition-all duration-200 hover:scale-[1.02] active:scale-95"
            >
              <span className="tracking-wide">{t.allCategories}</span>
            </Link>
            {categories.map((c) => {
              const label = lang === "ru" ? c.name_ru || c.name_uz : c.name_uz;
              return (
                <Link
                  key={c.id}
                  to={`/miniapp/catalog?category=${c.id}`}
                  className="shrink-0 flex items-center rounded-2xl border border-slate-200/90 bg-white px-4 py-2.5 text-[11.5px] font-bold text-[#172641] shadow-[0_1px_4px_rgba(0,0,0,0.03)] no-underline transition-all duration-200 hover:border-[#172641]/40 hover:shadow-md hover:-translate-y-0.5 active:scale-95"
                >
                  <span className="tracking-wide">{label}</span>
                </Link>
              );
            })}
          </div>"""
content = content.replace(old_home_categories, new_home_categories)

# 4. Remove icons from CatalogScreen category pills & use #172641
old_catalog_categories = """      {/* Category Pill Strip (Luxury Rounded Interactive Badges) */}
      <div className="no-scrollbar -mx-4 mt-3 flex items-center gap-2 overflow-x-auto px-4 pb-2">
        <button
          type="button"
          onClick={() => setSearchParams({})}
          className={`shrink-0 inline-flex items-center gap-2 rounded-2xl px-4 py-2.5 text-[11px] font-bold tracking-wide transition-all duration-200 cursor-pointer ${
            !selectedCat
              ? "bg-slate-900 text-white shadow-sm ring-1 ring-slate-900 scale-[1.02]"
              : "border border-slate-200/90 bg-white text-slate-800 shadow-xs hover:border-slate-300 hover:shadow-md hover:-translate-y-0.5 hover:text-black active:scale-95"
          }`}
        >
          <span className="text-sm drop-shadow-sm">✨</span>
          <span>{t.allCategories}</span>
        </button>
        {categories.map((c) => {
          const active = selectedCat === c.id;
          const label = lang === "ru" ? c.name_ru || c.name_uz : c.name_uz;
          const icon = getCategoryIcon(label);
          return (
            <button
              key={c.id}
              type="button"
              onClick={() => setSearchParams({ category: String(c.id) })}
              className={`shrink-0 inline-flex items-center gap-2 rounded-2xl px-4 py-2.5 text-[11px] font-bold tracking-wide transition-all duration-200 cursor-pointer ${
                active
                  ? "bg-gradient-to-r from-[#172641] via-[#223558] to-[#121c2e] text-[#faf7f2] shadow-[0_4px_16px_rgba(23,38,65,0.28)] ring-2 ring-[#c5a676] ring-offset-2 ring-offset-[#f6f2ea] scale-[1.02]"
                  : "border border-slate-200/90 bg-white text-slate-800 shadow-xs hover:border-slate-300 hover:shadow-md hover:-translate-y-0.5 hover:text-black active:scale-95"
              }`}
            >
              <span className="text-sm transition-transform duration-200 group-hover:scale-110">{icon}</span>
              <span>{label}</span>
            </button>
          );
        })}
      </div>"""

new_catalog_categories = """      {/* Category Pill Strip (Clean Typography without cheap emojis) */}
      <div className="no-scrollbar -mx-4 mt-3 flex items-center gap-2 overflow-x-auto px-4 pb-2">
        <button
          type="button"
          onClick={() => setSearchParams({})}
          className={`shrink-0 inline-flex items-center rounded-2xl px-4 py-2 text-[11.5px] font-bold tracking-wide transition-all duration-200 cursor-pointer ${
            !selectedCat
              ? "bg-[#172641] text-white shadow-sm ring-1 ring-[#172641] scale-[1.02]"
              : "border border-slate-200/90 bg-white text-[#172641] shadow-xs hover:border-[#172641]/40 hover:shadow-md hover:-translate-y-0.5 active:scale-95"
          }`}
        >
          <span>{t.allCategories}</span>
        </button>
        {categories.map((c) => {
          const active = selectedCat === c.id;
          const label = lang === "ru" ? c.name_ru || c.name_uz : c.name_uz;
          return (
            <button
              key={c.id}
              type="button"
              onClick={() => setSearchParams({ category: String(c.id) })}
              className={`shrink-0 inline-flex items-center rounded-2xl px-4 py-2 text-[11.5px] font-bold tracking-wide transition-all duration-200 cursor-pointer ${
                active
                  ? "bg-[#172641] text-white shadow-sm ring-1 ring-[#172641] scale-[1.02]"
                  : "border border-slate-200/90 bg-white text-[#172641] shadow-xs hover:border-[#172641]/40 hover:shadow-md hover:-translate-y-0.5 active:scale-95"
              }`}
            >
              <span>{label}</span>
            </button>
          );
        })}
      </div>"""
content = content.replace(old_catalog_categories, new_catalog_categories)

# 5. Update ProductCard to use #172641 for button and price
content = content.replace(
    'bg-slate-900 px-3 py-1.5 text-[10px] font-bold text-white shadow-xs transition-all duration-200 group-hover:bg-[#8a6c43]',
    'bg-[#172641] px-3.5 py-1.5 text-[10px] font-bold text-white shadow-xs transition-all duration-200 group-hover:bg-[#223558]'
)
content = content.replace(
    'text-slate-900 tracking-tight leading-none',
    'text-[#172641] tracking-tight leading-none'
)

# 6. Hero section button
content = content.replace(
    'bg-gradient-to-r from-[#d6bd92] via-[#e5d2ae] to-[#c5a676] px-6 py-3.5 text-[11px] font-bold uppercase tracking-[.18em] text-[#172641]',
    'bg-[#c5a676] hover:bg-[#d6bd92] px-6 py-3.5 text-[11px] font-bold uppercase tracking-[.18em] text-[#172641] shadow-[0_6px_20px_rgba(197,166,118,0.35)]'
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("MiniApp.tsx fully overhauled with #172641 and clean icons!")

