import re

with open(r'frontend\src\miniapp\MiniApp.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect HomeScreen in text
# First, add selectedCat state to HomeScreen
old_home_state = '''function HomeScreen({
  content,
  categories,
  customerName,
  favIds,
  onToggleFav,
}: {
  content: any;
  categories: any[];
  customerName?: string;
  favIds: number[];
  onToggleFav: (id: number) => void;
}) {
  const { lang, t } = useLang();
  const { toast } = useToast();
  const [featured, setFeatured] = useState<any[]>([]);
  const [lookbooks, setLookbooks] = useState<any[]>([]);
  const [addingBundleId, setAddingBundleId] = useState<number | null>(null);'''

new_home_state = '''function HomeScreen({
  content,
  categories,
  customerName,
  favIds,
  onToggleFav,
}: {
  content: any;
  categories: any[];
  customerName?: string;
  favIds: number[];
  onToggleFav: (id: number) => void;
}) {
  const { lang, t } = useLang();
  const { toast } = useToast();
  const [featured, setFeatured] = useState<any[]>([]);
  const [lookbooks, setLookbooks] = useState<any[]>([]);
  const [addingBundleId, setAddingBundleId] = useState<number | null>(null);
  const [selectedCatId, setSelectedCatId] = useState<number | "lookbook" | null>(null);'''

if old_home_state in text:
    text = text.replace(old_home_state, new_home_state)
    print("Replaced old_home_state successfully!")
else:
    print("Could not find old_home_state!")

# Next, remove the lookbook block that was above categories row, and integrate into categories and content area
# Find the section starting at {/* ---------------- BUY THE LOOK (LOOKBOOK BUNDLES) ---------------- */}
# down to {/* Editorial Luxury Category Chips Row */} and Featured / Collection Grid

pattern = re.compile(
    r'\{\/\* ---------------- BUY THE LOOK \(LOOKBOOK BUNDLES\) ---------------- \*\/\}[\s\S]*?\{\/\* Editorial Footer Note \*\/\}',
    re.MULTILINE
)

new_content_block = '''{/* Editorial Luxury Category Chips Row (Lookbook now in categories!) */}
      <section
        aria-label="Kategoriyalar"
        className="px-4 py-4"
      >
        <div className="flex items-center justify-between mb-2.5">
          <span className="text-[10px] font-bold uppercase tracking-[.2em] text-[#8a6c43]">
            {lang === "ru" ? "Коллекции и категории" : "Kolleksiyalar va bo‘limlar"}
          </span>
          <Link
            to="/miniapp/catalog"
            className="text-[11px] font-semibold text-slate-900 hover:underline"
          >
            {lang === "ru" ? "Весь каталог →" : "Barchasi →"}
          </Link>
        </div>
        <div className="flex gap-2 overflow-x-auto no-scrollbar pb-1">
          {/* Barchasi */}
          <button
            type="button"
            onClick={() => setSelectedCatId(null)}
            className={`shrink-0 flex items-center rounded-2xl px-4 py-2.5 text-[11.5px] font-bold transition-all duration-200 cursor-pointer ${
              selectedCatId === null
                ? "bg-[#172641] text-white shadow-sm ring-1 ring-[#172641] scale-[1.02]"
                : "border border-slate-200/90 bg-white text-[#172641] shadow-xs hover:border-[#172641]/40 hover:shadow-md hover:-translate-y-0.5 active:scale-95"
            }`}
          >
            <span className="tracking-wide">{t.allCategories}</span>
          </button>

          {/* Tayyor Obrazlar (Lookbook) Chip */}
          <button
            type="button"
            onClick={() => setSelectedCatId("lookbook")}
            className={`shrink-0 flex items-center gap-1.5 rounded-2xl px-4 py-2.5 text-[11.5px] font-bold transition-all duration-200 cursor-pointer ${
              selectedCatId === "lookbook"
                ? "bg-gradient-to-r from-[#172641] via-[#24375a] to-[#172641] text-[#faf7f2] shadow-sm ring-2 ring-[#c5a676] scale-[1.02]"
                : "border border-[#c5a676]/60 bg-[#fffdf9] text-[#172641] shadow-xs hover:border-[#c5a676] hover:shadow-md hover:-translate-y-0.5 active:scale-95"
            }`}
          >
            <span className="tracking-wide">{lang === "ru" ? "Готовые образы" : "Tayyor Obrazlar"}</span>
            <span className="text-[9px] font-extrabold uppercase bg-[#c5a676] text-slate-900 px-1.5 py-0.5 rounded-md shadow-2xs">
              -10%
            </span>
          </button>

          {/* Regular Categories */}
          {categories.map((c) => {
            const label = lang === "ru" ? c.name_ru || c.name_uz : c.name_uz;
            const active = selectedCatId === c.id;
            return (
              <button
                key={c.id}
                type="button"
                onClick={() => setSelectedCatId(c.id)}
                className={`shrink-0 flex items-center rounded-2xl px-4 py-2.5 text-[11.5px] font-bold transition-all duration-200 cursor-pointer ${
                  active
                    ? "bg-[#172641] text-white shadow-sm ring-1 ring-[#172641] scale-[1.02]"
                    : "border border-slate-200/90 bg-white text-[#172641] shadow-xs hover:border-[#172641]/40 hover:shadow-md hover:-translate-y-0.5 active:scale-95"
                }`}
              >
                <span className="tracking-wide">{label}</span>
              </button>
            );
          })}
        </div>
      </section>

      {/* Main Content Area based on Selected Category */}
      {selectedCatId === "lookbook" ? (
        /* LOOKBOOK BUNDLES VIEW */
        <section className="px-4 pt-1 rise-in">
          <div className="mb-4 flex items-end justify-between border-b border-[#c5a676]/30 pb-2.5">
            <div>
              <span className="text-[9px] font-bold uppercase tracking-[.22em] text-[#a4814d] block">
                WITHMORE STYLIST EDITORIAL
              </span>
              <h2 className="font-display text-[24px] font-bold text-[#172641]">
                {lang === "ru" ? "Готовые мужские образы" : "Tayyor erkaklar obrazlari"}
              </h2>
            </div>
            <span className="text-[10px] font-extrabold uppercase bg-[#172641] text-[#f5f1e8] px-3 py-1 rounded-full shadow-xs">
              -10% KOMPLEKT
            </span>
          </div>

          {lookbooks.length === 0 ? (
            <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center text-slate-500">
              Tayyor obrazlar tayyorlanmoqda...
            </div>
          ) : (
            <div className="space-y-4">
              {lookbooks.map((look: any) => (
                <div
                  key={look.id}
                  className="overflow-hidden rounded-2xl border border-[#c5a676]/30 bg-white shadow-sm hover:shadow-md transition-all"
                >
                  {/* Look Header */}
                  <div className="p-4 bg-gradient-to-r from-[#172641] to-[#25395b] text-[#f5f1e8] flex items-center justify-between">
                    <div>
                      <span className="text-[9px] font-bold uppercase tracking-[.2em] text-[#d6bd92]">
                        TAYYOR OBRAZ · JAMLANMA
                      </span>
                      <h3 className="font-display text-lg font-bold text-white">
                        {lang === "ru" ? look.title_ru || look.title_uz : look.title_uz}
                      </h3>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-slate-300 line-through block">
                        {formatPrice(look.regular_total)}
                      </span>
                      <span className="text-base font-extrabold text-[#d6bd92]">
                        {formatPrice(look.bundle_price)}
                      </span>
                    </div>
                  </div>

                  <div className="p-4 space-y-3">
                    <p className="text-xs text-slate-600 leading-relaxed">
                      {lang === "ru" ? look.description_ru || look.description_uz : look.description_uz}
                    </p>

                    {/* Included Items preview with fixed high-res images */}
                    <div className="grid grid-cols-3 gap-2 pt-1">
                      {look.items.map((it: any) => {
                        const imgUrl = it.image
                          ? (it.image.startsWith('/') || it.image.startsWith('http')
                              ? it.image
                              : `/uploads/${it.image}`)
                          : '';
                        return (
                          <Link
                            key={it.id}
                            to={`/miniapp/product/${it.id}`}
                            className="rounded-xl border border-slate-100 bg-[#faf8f3] p-2 text-center text-slate-900 no-underline hover:border-[#172641] transition group"
                          >
                            {imgUrl ? (
                              <div className="h-20 w-full overflow-hidden rounded-lg mb-1.5 bg-slate-100">
                                <img
                                  src={imgUrl}
                                  alt=""
                                  className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-300"
                                  onError={(e) => {
                                    (e.currentTarget as HTMLImageElement).style.display = 'none';
                                  }}
                                />
                              </div>
                            ) : (
                              <div className="h-20 w-full rounded-lg bg-slate-200 flex items-center justify-center text-xs mb-1.5">
                                👔
                              </div>
                            )}
                            <div className="text-[10.5px] font-bold truncate">
                              {lang === "ru" ? it.title_ru || it.title_uz : it.title_uz}
                            </div>
                            <div className="text-[9.5px] text-[#8a6c43] font-semibold mt-0.5">
                              {formatPrice(it.price)}
                            </div>
                          </Link>
                        );
                      })}
                    </div>

                    {/* Add Entire Look Button */}
                    <div className="pt-2">
                      <button
                        type="button"
                        disabled={addingBundleId === look.id}
                        onClick={() => handleAddBundle(look.id)}
                        className="w-full flex h-11 items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[#172641] to-[#25395b] hover:from-[#223555] hover:to-[#2e4770] text-[11px] font-bold uppercase tracking-[.14em] text-[#f5f1e8] shadow-sm transition active:scale-[.98] cursor-pointer"
                      >
                        <span>👔</span>
                        <span>
                          {addingBundleId === look.id
                            ? "Qo'shilmoqda..."
                            : `To'liq obrazni savatga qo'shish (-${look.discount_pct}% tejash)`}
                        </span>
                      </button>
                      <div className="mt-1 text-center text-[10px] text-slate-500 font-medium">
                        Komplekt chegirmasi orqali {formatPrice(look.savings)} tejab qolasiz
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      ) : (
        /* REGULAR PRODUCTS GRID VIEW */
        <section className="px-4 pt-2 rise-in">
          <div className="mb-4 flex items-end justify-between border-b border-slate-200/80 pb-2.5">
            <h2 className="font-display text-[24px] font-medium text-slate-900">
              {selectedCatId === null
                ? (featured.length > 0 ? t.featured : t.catalog)
                : (categories.find(c => c.id === selectedCatId)?.name_uz || t.catalog)}
            </h2>
            <Link
              to="/miniapp/catalog"
              className="text-[10px] font-bold uppercase tracking-[.16em] text-[#8a6c43] no-underline hover:underline"
            >
              {t.viewAll} · {allProds.length}
            </Link>
          </div>

          {loading ? (
            <SkeletonList count={4} />
          ) : (
            (() => {
              const activeProds = selectedCatId === null
                ? (featured.length > 0 ? featured : allProds).slice(0, 8)
                : allProds.filter(p => p.category_id === selectedCatId);

              if (activeProds.length === 0) {
                return <EmptyState text={t.emptyCatalog} />;
              }

              return (
                <div className="miniapp-product-grid">
                  {activeProds.map((p) => (
                    <ProductCard
                      key={p.id}
                      p={p}
                      isFav={favIds.includes(p.id)}
                      onToggleFav={onToggleFav}
                    />
                  ))}
                </div>
              );
            })()
          )}
        </section>
      )}

      {/* Editorial Footer Note */}'''

if pattern.search(text):
    text = pattern.sub(new_content_block, text)
    print("Pattern replaced successfully!")
else:
    print("Pattern not found!")

# Also add Tayyor Obrazlar to CatalogScreen category strip!
old_cat_strip = '''      {/* Category Pill Strip (Pure Typography, No Icons) */}
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
        </button>'''

new_cat_strip = '''      {/* Category Pill Strip (Pure Typography, No Icons) */}
      <div className="no-scrollbar -mx-4 mt-3 flex items-center gap-2 overflow-x-auto px-4 pb-2">
        <button
          type="button"
          onClick={() => setSearchParams({})}
          className={`shrink-0 inline-flex items-center rounded-2xl px-4 py-2 text-[11.5px] font-bold tracking-wide transition-all duration-200 cursor-pointer ${
            !selectedCat && searchParams.get("view") !== "lookbook"
              ? "bg-[#172641] text-white shadow-sm ring-1 ring-[#172641] scale-[1.02]"
              : "border border-slate-200/90 bg-white text-[#172641] shadow-xs hover:border-[#172641]/40 hover:shadow-md hover:-translate-y-0.5 active:scale-95"
          }`}
        >
          <span>{t.allCategories}</span>
        </button>
        <button
          type="button"
          onClick={() => setSearchParams({ view: "lookbook" })}
          className={`shrink-0 inline-flex items-center gap-1.5 rounded-2xl px-4 py-2 text-[11.5px] font-bold tracking-wide transition-all duration-200 cursor-pointer ${
            searchParams.get("view") === "lookbook"
              ? "bg-gradient-to-r from-[#172641] via-[#24375a] to-[#172641] text-[#faf7f2] shadow-sm ring-2 ring-[#c5a676] scale-[1.02]"
              : "border border-[#c5a676]/60 bg-[#fffdf9] text-[#172641] shadow-xs hover:border-[#c5a676] hover:shadow-md active:scale-95"
          }`}
        >
          <span>{lang === "ru" ? "Готовые образы" : "Tayyor Obrazlar"}</span>
          <span className="text-[9px] font-extrabold uppercase bg-[#c5a676] text-slate-900 px-1.5 py-0.5 rounded-md shadow-2xs">
            -10%
          </span>
        </button>'''

if old_cat_strip in text:
    text = text.replace(old_cat_strip, new_cat_strip)
    print("CatalogScreen category strip updated with Tayyor Obrazlar!")
else:
    print("Could not find old_cat_strip!")

with open(r'frontend\src\miniapp\MiniApp.tsx', 'w', encoding='utf-8') as f:
    f.write(text)

print("MiniApp.tsx updated successfully!")

