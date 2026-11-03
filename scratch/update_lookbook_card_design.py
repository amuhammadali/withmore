import re

with open(r'frontend\src\miniapp\MiniApp.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add LookbookCard component right after ProductCard component
lookbook_card_code = '''
// ---------------- LOOKBOOK CARD (MATCHES PRODUCT CARD 1:1) ----------------
function LookbookCard({
  look,
  onAddBundle,
  isAdding,
  onOpenDetail,
}: {
  look: any;
  onAddBundle: (id: number) => void;
  isAdding: boolean;
  onOpenDetail: (look: any) => void;
}) {
  const { lang, t } = useLang();
  const title = lang === "ru" ? look.title_ru || look.title_uz : look.title_uz;

  // Resolve cover photo: use first product image or look image
  const firstItemImg = look.items && look.items[0]?.image ? look.items[0].image : "";
  const rawImg = look.image || firstItemImg;
  const coverImg = rawImg
    ? (rawImg.startsWith("/") || rawImg.startsWith("http") ? rawImg : `/uploads/${rawImg}`)
    : "";

  return (
    <div
      onClick={() => onOpenDetail(look)}
      className="group relative min-w-0 self-start rise-in rounded-3xl border border-slate-200/80 bg-white p-2.5 shadow-[0_4px_20px_-4px_rgba(0,0,0,0.05)] transition-all duration-300 hover:-translate-y-1 hover:border-[#c5a676] hover:shadow-[0_16px_36px_-6px_rgba(15,23,42,0.12)] cursor-pointer"
    >
      <div className="relative aspect-[3/4] overflow-hidden rounded-[20px] bg-[#F1F3F7]">
        {coverImg ? (
          <img
            src={coverImg}
            alt={title}
            className="h-full w-full object-cover transition-transform duration-700 ease-out group-hover:scale-106"
            onError={(e) => {
              (e.currentTarget as HTMLImageElement).style.display = "none";
            }}
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-4xl bg-[#172641] text-[#c5a676]">
            👔
          </div>
        )}

        {/* Top-left Lookbook Badge */}
        <div className="absolute left-2.5 top-2.5 flex items-center gap-1.5 rounded-full bg-white/92 backdrop-blur-md px-2.5 py-1 text-[9px] font-bold uppercase tracking-wider text-slate-800 shadow-xs border border-white/70">
          <span className="h-1.5 w-1.5 rounded-full bg-[#c5a676] animate-pulse" />
          <span>OBRAZ · -{look.discount_pct}%</span>
        </div>

        {/* Bottom pieces preview pill */}
        <div className="absolute bottom-2.5 left-2.5 right-2.5 flex items-center justify-between rounded-xl bg-slate-950/70 backdrop-blur-md px-2.5 py-1 text-[9px] font-semibold text-white/95">
          <span>{look.items?.length || 3} ta kiyim jamlanmasi</span>
          <span className="text-[#d6bd92] font-bold">-{look.discount_pct}%</span>
        </div>
      </div>

      <div className="mt-2.5 px-1">
        <div className="text-[9px] font-bold tracking-[0.16em] uppercase text-[#a4814d] truncate">
          TAYYOR OBRAZ · LOOKBOOK
        </div>
        <div className="font-display text-[14px] sm:text-[15px] font-semibold text-slate-900 line-clamp-1 group-hover:text-[#8a6c43] transition-colors mt-0.5">
          {title}
        </div>

        {/* Mini item list pills */}
        <div className="mt-1 flex flex-wrap gap-1">
          {look.items?.slice(0, 3).map((it: any) => (
            <span key={it.id} className="text-[8.5px] font-medium bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded-md truncate max-w-[110px]">
              {it.title_uz}
            </span>
          ))}
        </div>

        <div className="mt-2 flex items-center justify-between gap-1 pt-1.5 border-t border-slate-100">
          <div className="flex flex-col">
            <span className="text-[8.5px] uppercase tracking-wider font-semibold text-slate-400 line-through leading-none">
              {formatPrice(look.regular_total)}
            </span>
            <span className="text-[13px] sm:text-[14px] font-black text-[#172641] tracking-tight leading-none mt-0.5">
              {formatPrice(look.bundle_price)}
            </span>
          </div>
          <button
            type="button"
            disabled={isAdding}
            onClick={(e) => {
              e.stopPropagation();
              onAddBundle(look.id);
            }}
            className="inline-flex items-center gap-1 rounded-full bg-[#172641] px-3.5 py-1.5 text-[10px] font-bold text-white shadow-xs transition-all duration-200 group-hover:bg-[#223558] group-hover:scale-105 active:scale-95 cursor-pointer"
          >
            <span>{isAdding ? "..." : "Savatga"}</span>
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </button>
        </div>
      </div>
    </div>
  );
}
'''

# Insert LookbookCard right after ProductCard in text
target_insert = 'function ProductCard('
if target_insert in text:
    # Find closing of ProductCard
    idx_start = text.find(target_insert)
    # Let's insert lookbook_card_code before ProductCard
    text = text[:idx_start] + lookbook_card_code + "\n" + text[idx_start:]
    print("Inserted LookbookCard successfully!")
else:
    print("Could not find ProductCard!")

# 2. In HomeScreen, update lookbook rendering to use miniapp-product-grid and LookbookCard!
# Also add activeLookbookDetail state to HomeScreen
old_hs_state = '  const [selectedCatId, setSelectedCatId] = useState<number | "lookbook" | null>(null);'
new_hs_state = '''  const [selectedCatId, setSelectedCatId] = useState<number | "lookbook" | null>(null);
  const [activeLookbookDetail, setActiveLookbookDetail] = useState<any>(null);'''

if old_hs_state in text:
    text = text.replace(old_hs_state, new_hs_state)
    print("Added activeLookbookDetail state to HomeScreen!")

# Now replace the Lookbook section in HomeScreen with miniapp-product-grid
old_lookbook_view_pattern = re.compile(
    r'\{\/\* LOOKBOOK BUNDLES VIEW \*\/\}[\s\S]*?\{\/\* REGULAR PRODUCTS GRID VIEW \*\/\}',
    re.MULTILINE
)

new_lookbook_grid_view = '''{/* LOOKBOOK BUNDLES VIEW (MATCHES PRODUCT GRID EXACTLY) */}
        <section className="px-4 pt-1 rise-in">
          <div className="mb-4 flex items-end justify-between border-b border-slate-200/80 pb-2.5">
            <div>
              <h2 className="font-display text-[24px] font-medium text-slate-900">
                {lang === "ru" ? "Готовые мужские образы" : "Tayyor erkaklar obrazlari"}
              </h2>
              <span className="text-[10px] font-bold uppercase tracking-[.16em] text-[#a4814d] block mt-0.5">
                Stilistlar tavsiyasi · Komplekt chegirmasi
              </span>
            </div>
            <span className="text-[10px] font-extrabold uppercase bg-[#172641] text-[#f5f1e8] px-3 py-1 rounded-full shadow-xs">
              -10% KOMPLEKT
            </span>
          </div>

          {lookbooks.length === 0 ? (
            <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center text-slate-500 text-xs">
              Tayyor obrazlar tayyorlanmoqda...
            </div>
          ) : (
            <div className="miniapp-product-grid">
              {lookbooks.map((look: any) => (
                <LookbookCard
                  key={look.id}
                  look={look}
                  onAddBundle={handleAddBundle}
                  isAdding={addingBundleId === look.id}
                  onOpenDetail={setActiveLookbookDetail}
                />
              ))}
            </div>
          )}

          {/* Lookbook Detail Sheet Modal */}
          {activeLookbookDetail && (
            <div
              className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 backdrop-blur-xs p-0 sm:p-4 animate-in fade-in duration-200"
              onClick={() => setActiveLookbookDetail(null)}
            >
              <div
                className="w-full max-w-lg rounded-t-3xl sm:rounded-3xl border border-slate-200 bg-white p-5 shadow-2xl space-y-4 max-h-[88vh] overflow-y-auto no-scrollbar"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <div>
                    <span className="text-[9px] font-bold uppercase tracking-[.2em] text-[#c5a676] block">
                      TAYYOR OBRAZ TAFSILOTLARI
                    </span>
                    <h3 className="font-display text-lg font-bold text-[#172641]">
                      {lang === "ru" ? activeLookbookDetail.title_ru || activeLookbookDetail.title_uz : activeLookbookDetail.title_uz}
                    </h3>
                  </div>
                  <button
                    type="button"
                    onClick={() => setActiveLookbookDetail(null)}
                    className="h-8 w-8 rounded-full bg-slate-100 text-slate-600 flex items-center justify-center font-bold text-sm cursor-pointer hover:bg-slate-200"
                  >
                    ✕
                  </button>
                </div>

                <p className="text-xs text-slate-600 leading-relaxed">
                  {lang === "ru" ? activeLookbookDetail.description_ru || activeLookbookDetail.description_uz : activeLookbookDetail.description_uz}
                </p>

                <div className="space-y-2 pt-1">
                  <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Jamlanmaga kiruvchi mahsulotlar ({activeLookbookDetail.items?.length || 0} ta):
                  </div>
                  <div className="space-y-2">
                    {activeLookbookDetail.items?.map((it: any) => {
                      const img = it.image ? (it.image.startsWith('/') || it.image.startsWith('http') ? it.image : `/uploads/${it.image}`) : '';
                      return (
                        <Link
                          key={it.id}
                          to={`/miniapp/product/${it.id}`}
                          className="flex items-center gap-3 rounded-2xl border border-slate-100 bg-[#faf8f3] p-2.5 no-underline text-slate-900 hover:border-[#172641] transition"
                        >
                          {img ? (
                            <img src={img} alt="" className="h-14 w-12 rounded-xl object-cover" />
                          ) : (
                            <div className="h-14 w-12 rounded-xl bg-slate-200 flex items-center justify-center text-sm">👔</div>
                          )}
                          <div className="flex-1 min-w-0">
                            <div className="text-xs font-bold truncate">{lang === "ru" ? it.title_ru || it.title_uz : it.title_uz}</div>
                            {it.sizes?.length > 0 && (
                              <div className="text-[10px] text-slate-500 mt-0.5">O'lchamlar: {it.sizes.join(', ')}</div>
                            )}
                          </div>
                          <div className="text-right">
                            <div className="text-xs font-bold text-[#172641]">{formatPrice(it.price)}</div>
                            <span className="text-[9.5px] text-[#c5a676] font-semibold">Batafsil →</span>
                          </div>
                        </Link>
                      );
                    })}
                  </div>
                </div>

                <div className="rounded-2xl bg-gradient-to-br from-[#172641] to-[#25395b] p-4 text-[#faf7f2] space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-[10px] text-slate-300">Alohida sotib olinsa:</div>
                      <div className="text-xs line-through text-slate-400">{formatPrice(activeLookbookDetail.regular_total)}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-[10px] text-[#d6bd92] font-bold">Komplekt narxi (-{activeLookbookDetail.discount_pct}%):</div>
                      <div className="text-base font-black text-[#d6bd92]">{formatPrice(activeLookbookDetail.bundle_price)}</div>
                    </div>
                  </div>

                  <button
                    type="button"
                    disabled={addingBundleId === activeLookbookDetail.id}
                    onClick={() => {
                      handleAddBundle(activeLookbookDetail.id);
                      setActiveLookbookDetail(null);
                    }}
                    className="w-full flex h-11 items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[#d6bd92] to-[#c5a676] hover:brightness-105 text-slate-900 text-xs font-bold uppercase tracking-wider shadow-sm transition cursor-pointer"
                  >
                    <span>👔</span>
                    <span>To'liq obrazni savatga qo'shish (Tejov: {formatPrice(activeLookbookDetail.savings)})</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </section>
      ) : (
        /* REGULAR PRODUCTS GRID VIEW */'''

if old_lookbook_view_pattern.search(text):
    text = old_lookbook_view_pattern.sub(new_lookbook_grid_view, text)
    print("Replaced old lookbook view with LookbookCard miniapp-product-grid!")
else:
    print("Could not find old_lookbook_view_pattern!")

with open(r'frontend\src\miniapp\MiniApp.tsx', 'w', encoding='utf-8') as f:
    f.write(text)

print("MiniApp.tsx updated successfully with LookbookCard matching ProductCard!")

