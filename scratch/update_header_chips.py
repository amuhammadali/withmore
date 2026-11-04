file_path = r"frontend/src/miniapp/MiniApp.tsx"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

target = """          <div className="mb-4 flex items-end justify-between border-b border-slate-200/80 pb-2.5">
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
          </div>"""

replacement = """          <div className="mb-3.5 flex flex-wrap items-center justify-between gap-2 border-b border-slate-200/80 pb-2.5">
            <div>
              <h2 className="font-display text-[20px] font-semibold text-slate-900">
                {selectedCatId === null
                  ? (lang === "ru" ? "Все товары" : "Tanlangan modellar")
                  : (categories.find(c => c.id === selectedCatId)?.name_uz || "Kolleksiya")}
              </h2>
            </div>

            {/* Quick Filter Pills (Yangi / Xit / Chegirma) */}
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

code = code.replace(target, replacement)
code = code.replace(target.replace("\n", "\r\n"), replacement.replace("\n", "\r\n"))

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated product grid header with quick filter chips successfully!")

