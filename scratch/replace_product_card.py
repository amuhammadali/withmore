file_path = r"frontend/src/miniapp/MiniApp.tsx"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

target = """    <div className="group relative min-w-0 self-start rise-in rounded-3xl border border-slate-200/80 bg-white p-2.5 shadow-[0_4px_20px_-4px_rgba(0,0,0,0.05)] transition-all duration-300 hover:-translate-y-1 hover:border-slate-300 hover:shadow-[0_16px_36px_-6px_rgba(15,23,42,0.12)]">
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
              <span className="text-[13px] sm:text-[14px] font-black text-[#172641] tracking-tight leading-none">
                {formatPrice(p.price)}
              </span>
            </div>
            <span className="inline-flex items-center gap-1 rounded-full bg-[#172641] px-3.5 py-1.5 text-[10px] font-bold text-white shadow-xs transition-all duration-200 group-hover:bg-[#223558] group-hover:scale-105 active:scale-95">
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
    </div>"""

replacement = """    <div className="group relative min-w-0 self-start rise-in rounded-2xl border border-slate-200/90 bg-white overflow-hidden shadow-2xs transition-all duration-200 hover:border-slate-300 hover:shadow-md flex flex-col w-full">
      <Link
        to={`/miniapp/product/${p.id}`}
        className="block w-full min-w-0 text-left no-underline text-slate-900"
      >
        {/* ONE23 Aspect Ratio 5/6 Image Box */}
        <div className="relative aspect-[5/6] w-full overflow-hidden bg-[#F2F4F8]">
          <ProductImage
            src={p.thumb}
            alt={name}
            className="h-full w-full object-cover transition-transform duration-500 ease-out group-hover:scale-104"
          />

          {/* Top-left ONE23 Badge */}
          <div className="absolute left-2 top-2 flex items-center gap-1 rounded-md bg-white/95 backdrop-blur-xs px-2 py-0.5 text-[9.5px] font-bold uppercase tracking-wider text-slate-800 shadow-2xs border border-white/80">
            <span className={`h-1.5 w-1.5 rounded-full ${isStock ? "bg-emerald-500" : "bg-amber-500"}`} />
            <span>{isStock ? (lang === "ru" ? "В наличии" : "Mavjud") : (lang === "ru" ? "Предзаказ" : "Buyurtmaga")}</span>
          </div>

          {/* Sold out overlay */}
          {p.sold_out && (
            <div className="absolute inset-0 flex items-center justify-center bg-slate-950/60 backdrop-blur-2xs">
              <span className="rounded-md bg-white px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-900 shadow-sm">
                {t.soldOut}
              </span>
            </div>
          )}
        </div>

        {/* ONE23 Card Body */}
        <div className="p-2 sm:p-2.5 flex flex-col flex-1 gap-1">
          <h3 className="text-xs sm:text-[13px] font-medium text-slate-900 line-clamp-2 leading-snug group-hover:text-[#172641]">
            {name}
          </h3>

          <div className="mt-0.5 text-[13px] sm:text-sm font-bold text-slate-900 tabular-nums">
            {formatPrice(p.price)}
          </div>

          <div className="mt-auto pt-1.5">
            <span className="w-full h-8 sm:h-8.5 rounded-xl bg-[#172641] hover:bg-[#223558] text-white text-[11px] font-semibold flex items-center justify-center gap-1.5 transition active:scale-95 shadow-2xs">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="9" cy="20" r="1.5" />
                <circle cx="18" cy="20" r="1.5" />
                <path d="M3 4h2l2.5 12h12l2-8H6" />
              </svg>
              <span>{lang === "ru" ? "В корзину" : "Savatga"}</span>
            </span>
          </div>
        </div>
      </Link>

      {/* Top-right ONE23 Floating Favorite Button */}
      <button
        type="button"
        aria-label={t.favorites}
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          onToggleFav(p.id);
        }}
        className="absolute top-2 right-2 flex h-7.5 w-7.5 items-center justify-center rounded-full bg-white/90 text-slate-600 shadow-xs backdrop-blur-xs transition hover:scale-110 hover:text-[#a3463c] active:scale-90 cursor-pointer border border-white/70"
      >
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill={isFav ? "#a3463c" : "none"}
          stroke={isFav ? "#a3463c" : "currentColor"}
          strokeWidth="2"
        >
          <path d="M12 21s-7-4.5-9.5-9A5.5 5.5 0 0 1 12 6a5.5 5.5 0 0 1 9.5 6c-2.5 4.5-9.5 9-9.5 9z" />
        </svg>
      </button>
    </div>"""

if target in code:
    code = code.replace(target, replacement, 1)
    print("ProductCard replaced successfully!")
else:
    print("Target not found, checking whitespace differences...")
    target_norm = target.replace("\r\n", "\n")
    code_norm = code.replace("\r\n", "\n")
    if target_norm in code_norm:
        code_norm = code_norm.replace(target_norm, replacement.replace("\r\n", "\n"), 1)
        code = code_norm
        print("ProductCard replaced with normalized newlines!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

