import os

file_path = r"c:\Users\muham\OneDrive\Desktop\withmore\frontend\src\miniapp\MiniApp.tsx"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Language switcher styling in header
content = content.replace(
    'className="flex rounded-full border border-[#172641]/15 p-0.5 text-[10px] font-bold bg-[#fbf8f2]"',
    'className="flex rounded-full border border-slate-200 bg-slate-100/80 p-0.5 text-[10px] font-bold"'
)
content = content.replace(
    'bg-[#172641] text-[#f4efe5]',
    'bg-slate-900 text-white shadow-xs'
)
content = content.replace(
    'bg-transparent text-[#172641]/60',
    'bg-transparent text-slate-500 hover:text-slate-900'
)

# 2. Update Nav capsule container
content = content.replace(
    'border border-[#d6bd92]/35 bg-[#172641]/95 p-1.5 text-[#f4efe5] shadow-[0_18px_42px_-8px_rgba(14,24,42,0.55),0_0_0_1px_rgba(255,255,255,0.07)_inset] backdrop-blur-xl',
    'border border-white/10 bg-[#0F172A]/92 p-1.5 text-slate-300 shadow-[0_20px_45px_rgba(0,0,0,0.35)] backdrop-blur-2xl'
)

# 3. Update NavTab styling
content = content.replace(
    'bg-gradient-to-b from-[#ebdcc0] to-[#cfa972] text-[#172641] shadow-[0_6px_18px_-3px_rgba(214,189,146,0.45)]',
    'bg-gradient-to-b from-[#e5d2ae] to-[#c5a676] text-[#0F172A] font-bold shadow-[0_4px_16px_rgba(197,166,118,0.4)]'
)
content = content.replace(
    'text-[#f4efe5]/70 hover:bg-white/10 hover:text-[#f4efe5]',
    'text-slate-400 hover:bg-white/10 hover:text-white'
)
content = content.replace(
    'bg-[#d6bd92] text-[#172641]',
    'bg-[#c5a676] text-[#0F172A]'
)

# 4. Replace ProductCard
old_product_card_start = "function ProductCard({"
old_product_card_end = "// ---------------- LUXURY BRAND LOGO MARQUEE TICKER ----------------"

start_idx = content.find(old_product_card_start)
end_idx = content.find(old_product_card_end)

if start_idx != -1 and end_idx != -1:
    new_product_card = """function ProductCard({
  p,
  isFav,
  onToggleFav,
}: {
  p: any;
  isFav: boolean;
  onToggleFav: (id: number) => void;
}) {
  const { lang, t } = useLang();
  const name = lang === "ru" ? p.name_ru || p.name_uz : p.name_uz;
  const isStock = p.sale_type === "stock";

  return (
    <div className="group relative min-w-0 self-start rise-in rounded-3xl border border-slate-200/80 bg-white p-2.5 shadow-[0_4px_20px_-4px_rgba(0,0,0,0.05)] transition-all duration-300 hover:-translate-y-1 hover:border-slate-300 hover:shadow-[0_16px_36px_-6px_rgba(15,23,42,0.12)]">
      <Link
        to={`/miniapp/product/${p.id}`}
        className="block w-full min-w-0 text-left no-underline text-slate-900"
      >
        <div className="relative aspect-[3/4] overflow-hidden rounded-[20px] bg-[#F1F3F7]">
          <ProductImage
            src={p.thumb}
            alt={name}
            className="h-full w-full object-cover transition-transform duration-700 ease-out group-hover:scale-106"
          />

          {/* Top-left Sale Type Badge */}
          <div className="absolute left-2.5 top-2.5 flex items-center gap-1.5 rounded-full bg-white/92 backdrop-blur-md px-2.5 py-1 text-[9px] font-bold uppercase tracking-wider text-slate-800 shadow-xs border border-white/70">
            <span className={`h-1.5 w-1.5 rounded-full ${isStock ? "bg-emerald-500 animate-pulse" : "bg-amber-500"}`} />
            <span>{isStock ? t.inStockBadge : t.preorderBadge}</span>
          </div>

          {/* Sold out bottom bar */}
          {p.sold_out && (
            <div className="absolute inset-0 flex items-center justify-center bg-slate-950/60 backdrop-blur-[2px]">
              <span className="rounded-full bg-white px-3 py-1 text-[10px] font-extrabold uppercase tracking-widest text-slate-900 shadow-md">
                {t.soldOut}
              </span>
            </div>
          )}
        </div>

        <div className="mt-2.5 px-1">
          <div className="text-[9px] font-bold tracking-[0.16em] uppercase text-slate-400 truncate">
            WITHMORE BESPOKE
          </div>
          <div className="font-display text-[14px] sm:text-[15px] font-semibold text-slate-900 line-clamp-1 group-hover:text-[#8a6c43] transition-colors mt-0.5">
            {name}
          </div>
          <div className="mt-2 flex items-center justify-between gap-1 pt-1.5 border-t border-slate-100">
            <div className="flex flex-col">
              <span className="text-[8.5px] uppercase tracking-wider font-semibold text-slate-400">Narx</span>
              <span className="text-[13px] sm:text-[14px] font-black text-slate-900 tracking-tight leading-none">
                {formatPrice(p.price)}
              </span>
            </div>
            <span className="inline-flex items-center gap-1 rounded-full bg-slate-900 px-3 py-1.5 text-[10px] font-bold text-white shadow-xs transition-all duration-200 group-hover:bg-[#8a6c43] group-hover:scale-105 active:scale-95">
              <span>Tanlash</span>
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </span>
          </div>
        </div>
      </Link>

      {/* Top-right Favorite Heart Button */}
      <button
        type="button"
        aria-label={t.favorites}
        onClick={(e) => {
          e.stopPropagation();
          onToggleFav(p.id);
        }}
        className="absolute right-2.5 top-2.5 flex h-8 w-8 items-center justify-center rounded-full bg-white/90 backdrop-blur-md text-slate-700 shadow-xs border border-white/70 transition-all duration-200 hover:scale-110 active:scale-90 hover:bg-white cursor-pointer"
      >
        <svg
          width="15"
          height="15"
          viewBox="0 0 24 24"
          fill={isFav ? "#e11d48" : "none"}
          stroke={isFav ? "#e11d48" : "currentColor"}
          strokeWidth="2"
        >
          <path d="M12 21s-7-4.5-9.5-9A5.5 5.5 0 0 1 12 6a5.5 5.5 0 0 1 9.5 6c-2.5 4.5-9.5 9-9.5 9z" />
        </svg>
      </button>
    </div>
  );
}

"""
    content = content[:start_idx] + new_product_card + content[end_idx:]
    print("ProductCard replaced successfully!")
else:
    print(f"ProductCard markers not found: start={start_idx}, end={end_idx}")

# 5. Highlights section
old_highlights = """      {/* Atelier Excellence Highlights */}
      <section className="mx-4 mt-3 mb-1 rounded-2xl border border-[#dccab0]/70 bg-gradient-to-br from-[#faf7f2] via-[#f7f2e7] to-[#efe6d5] p-3 shadow-xs">
        <div className="grid grid-cols-3 gap-2 text-center divide-x divide-[#dccab0]/60">
          <div className="px-1">
            <div className="text-sm mb-0.5">✂️</div>
            <div className="text-[10px] font-extrabold text-[#172641]">Aniq Bichim</div>
            <div className="text-[8px] font-medium text-[#7d8aa3] mt-0.5">Qaddi-qomatga mos</div>
          </div>
          <div className="px-1">
            <div className="text-sm mb-0.5">🇮🇹</div>
            <div className="text-[10px] font-extrabold text-[#172641]">100% Original</div>
            <div className="text-[8px] font-medium text-[#7d8aa3] mt-0.5">Italiya & Angliya</div>
          </div>
          <div className="px-1">
            <div className="text-sm mb-0.5">⚡</div>
            <div className="text-[10px] font-extrabold text-[#172641]">Tezkor Kuryer</div>
            <div className="text-[8px] font-medium text-[#7d8aa3] mt-0.5">Butun O‘zbekiston</div>
          </div>
        </div>
      </section>"""

new_highlights = """      {/* Atelier Excellence Highlights */}
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
content = content.replace(old_highlights, new_highlights)

# 6. Categories row in HomeScreen
content = content.replace(
    'bg-gradient-to-r from-[#172641] via-[#223558] to-[#121c2e] px-4 py-2.5 text-[11px] font-bold text-[#faf7f2] shadow-[0_4px_16px_rgba(23,38,65,0.28)] ring-2 ring-[#c5a676] ring-offset-2 ring-offset-[#f6f2ea]',
    'bg-slate-900 px-4 py-2.5 text-[11px] font-bold text-white shadow-sm ring-1 ring-slate-900'
)
content = content.replace(
    'border border-[#dccab0] bg-gradient-to-b from-white to-[#fbf7f0] px-4 py-2.5 text-[11px] font-bold text-[#172641] shadow-[0_2px_8px_rgba(23,38,65,0.04)] no-underline transition-all duration-200 hover:border-[#c5a676] hover:shadow-[0_6px_20px_rgba(197,166,118,0.28)] hover:-translate-y-0.5 hover:text-[#0b1728]',
    'border border-slate-200/90 bg-white px-4 py-2.5 text-[11px] font-bold text-slate-800 shadow-[0_1px_4px_rgba(0,0,0,0.03)] no-underline transition-all duration-200 hover:border-slate-300 hover:shadow-md hover:-translate-y-0.5 hover:text-black'
)

# 7. Section dividers & titles
content = content.replace(
    'border-b border-[#172641]/15 pb-2.5',
    'border-b border-slate-200/80 pb-2.5'
)
content = content.replace(
    'border-t border-[#172641]/15 pt-6',
    'border-t border-slate-200/80 pt-6'
)
content = content.replace(
    'text-[#172641]',
    'text-slate-900'
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated MiniApp.tsx successfully!")

