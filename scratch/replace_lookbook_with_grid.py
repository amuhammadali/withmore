with open(r'frontend\src\miniapp\MiniApp.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

start_marker = '{/* Main Content Area based on Selected Category */}'
end_marker = '{/* REGULAR PRODUCTS GRID VIEW */}'

start_idx = text.find(start_marker)
end_idx = text.find(end_marker)

print("start_idx:", start_idx, "end_idx:", end_idx)
if start_idx != -1 and end_idx != -1:
    old_block = text[start_idx:end_idx]
    
    new_block = '''{/* Main Content Area based on Selected Category */}
      {selectedCatId === "lookbook" ? (
        /* LOOKBOOK BUNDLES VIEW (MATCHES PRODUCT GRID 1:1) */
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
        '''
    text = text[:start_idx] + new_block + text[end_idx:]
    with open(r'frontend\src\miniapp\MiniApp.tsx', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Replaced lookbook view with LookbookCard in miniapp-product-grid!")
else:
    print("Markers not found!")

