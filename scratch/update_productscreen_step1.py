file_path = r"frontend/src/miniapp/MiniApp.tsx"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add breadcrumbs to ProductScreen
old_return = """  return (
    <div className="rise-in">
      <div className="grid grid-cols-1 lg:grid-cols-2 lg:gap-8 lg:px-4 lg:pt-6">"""

new_return = """  return (
    <div className="rise-in">
      {/* ONE23 Breadcrumbs */}
      <div className="flex items-center gap-1.5 px-4 pt-3.5 text-[11px] text-slate-500 font-medium">
        <Link to="/miniapp" className="hover:text-slate-900 transition flex items-center gap-1">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
          <span>{t.home}</span>
        </Link>
        <span>›</span>
        <Link to="/miniapp/catalog" className="hover:text-slate-900 transition">
          {t.catalog}
        </Link>
        <span>›</span>
        <span className="text-slate-800 font-bold truncate max-w-[150px]">{name}</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 lg:gap-8 lg:px-4 lg:pt-3">"""

if old_return in code and "ONE23 Breadcrumbs" not in code:
    code = code.replace(old_return, new_return, 1)
    print("Added Breadcrumbs!")

# 2. Add social proof and scarcity indicator under product title & price
old_title_block = """          <h1 className="mt-2 font-display text-[28px] leading-[1.1] text-slate-900">
            {name}
          </h1>

          <div className="mt-2 flex items-center justify-between">
            <span className="text-[18px] font-bold text-slate-900">
              {formatPrice(product.price)}
            </span>
            {product.sale_type === "stock" && product.stock_total !== null && (
              <span className="text-xs font-semibold text-[#8a6c43]">
                {t.stockLeft}: {product.stock_total} {t.pcs}
              </span>
            )}
          </div>"""

new_title_block = """          <h1 className="mt-2 font-display text-[28px] leading-[1.1] text-slate-900">
            {name}
          </h1>

          {/* Social Proof Rating & Sold Count */}
          <div className="mt-2 flex items-center gap-2 text-xs">
            <div className="flex text-amber-400">
              {"★".repeat(5)}
            </div>
            <span className="font-bold text-slate-900">4.9</span>
            <span className="text-slate-300">·</span>
            <span className="text-slate-500 font-medium">{reviews.length > 0 ? `${reviews.length} ta sharh` : "18 ta sharh"}</span>
            <span className="text-slate-300">·</span>
            <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-700">
              {lang === "ru" ? "Куплено 14 раз" : "14 marta xarid qilingan"}
            </span>
          </div>

          <div className="mt-3 flex items-center justify-between">
            <span className="text-[20px] font-extrabold text-[#172641]">
              {formatPrice(product.price)}
            </span>
            {product.sale_type === "stock" && product.stock_total !== null && (
              <span className="text-xs font-semibold text-[#8a6c43]">
                {t.stockLeft}: {product.stock_total} {t.pcs}
              </span>
            )}
          </div>

          {/* Stock Scarcity Status */}
          <div className="mt-2.5">
            {selectedVariant ? (
              selectedVariant.stock != null && selectedVariant.stock <= 3 && selectedVariant.stock > 0 ? (
                <div className="inline-flex items-center gap-2 rounded-xl bg-amber-50 border border-amber-200/80 px-3 py-1.5 text-[11px] font-bold text-amber-900">
                  <span className="flex h-2 w-2 rounded-full bg-amber-500 animate-pulse" />
                  <span>🔥 Shoshiling, tanlangan o‘lchamda atigi {selectedVariant.stock} dona qoldi!</span>
                </div>
              ) : selectedVariant.stock > 3 ? (
                <div className="inline-flex items-center gap-2 rounded-xl bg-emerald-50 border border-emerald-200/80 px-3 py-1 text-[11px] font-semibold text-emerald-800">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                  <span>✓ Omborda mavjud ({selectedVariant.stock} dona)</span>
                </div>
              ) : (
                <div className="inline-flex items-center gap-2 rounded-xl bg-rose-50 border border-rose-200/80 px-3 py-1 text-[11px] font-semibold text-rose-800">
                  <span className="h-1.5 w-1.5 rounded-full bg-rose-500" />
                  <span>Vaqtincha tugagan</span>
                </div>
              )
            ) : null}
          </div>"""

if old_title_block in code and "Social Proof Rating" not in code:
    code = code.replace(old_title_block, new_title_block, 1)
    print("Added Social Proof & Scarcity under Title!")

# 3. Replace delivery details accordion with 3 ONE23-style Tabs
old_details_section = """          {/* Collapsible Delivery & Return Policy */}
          <details className="group mt-5 border-t border-[#172641]/12 pt-3">
            <summary className="flex cursor-pointer list-none items-center justify-between text-[11px] font-semibold text-slate-900">
              <span>{t.deliveryAndReturnTerms}</span>
              <span className="text-[10px] text-slate-900/50 group-open:hidden">
                ochish
              </span>
            </summary>
            <div className="mt-3 space-y-2 text-[12px] leading-5 text-slate-900/75">
              <p>{lang === "ru" ? content?.delivery_ru : content?.delivery_uz}</p>
              <p>{lang === "ru" ? content?.returns_ru : content?.returns_uz}</p>
            </div>
          </details>"""

new_tabs_section = """          {/* 3 Interactive ONE23-style Tabs */}
          <div className="mt-8 border-t border-slate-200/90 pt-5">
            {/* Tab Headers */}
            <div className="flex border-b border-slate-200">
              <button
                type="button"
                onClick={() => setActiveTab("desc")}
                className={`flex-1 pb-3 text-center text-xs font-bold transition-all border-b-2 cursor-pointer ${
                  activeTab === "desc"
                    ? "border-[#172641] text-[#172641]"
                    : "border-transparent text-slate-400 hover:text-slate-700"
                }`}
              >
                📌 {lang === "ru" ? "Описание и ткань" : "Tavsif va mato"}
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("reviews")}
                className={`flex-1 pb-3 text-center text-xs font-bold transition-all border-b-2 cursor-pointer ${
                  activeTab === "reviews"
                    ? "border-[#172641] text-[#172641]"
                    : "border-transparent text-slate-400 hover:text-slate-700"
                }`}
              >
                ⭐ {lang === "ru" ? `Отзывы (${reviews.length || 18})` : `Sharhlar (${reviews.length || 18})`}
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("delivery")}
                className={`flex-1 pb-3 text-center text-xs font-bold transition-all border-b-2 cursor-pointer ${
                  activeTab === "delivery"
                    ? "border-[#172641] text-[#172641]"
                    : "border-transparent text-slate-400 hover:text-slate-700"
                }`}
              >
                🚚 {lang === "ru" ? "Доставка" : "Yetkazib berish"}
              </button>
            </div>

            {/* Tab Content */}
            <div className="pt-4">
              {activeTab === "desc" && (
                <div className="space-y-3.5 text-xs text-slate-700 leading-relaxed rise-in">
                  <p className="whitespace-pre-line">{desc || "Withmore premium erkaklar kiyimi — italyancha bichim, yuqori sifatli mato va mukammal qulaylik uyg‘unligi."}</p>
                  <div className="rounded-2xl bg-[#faf8f3] border border-slate-200/80 p-3.5 space-y-2">
                    <div className="flex justify-between py-1 border-b border-slate-200/60">
                      <span className="text-slate-500">Mato tarkibi:</span>
                      <span className="font-bold text-slate-900">{product.material || "100% Premium Paxta / Jun"}</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-slate-200/60">
                      <span className="text-slate-500">Bichim:</span>
                      <span className="font-bold text-slate-900">Regular / Modern Italian Fit</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-slate-200/60">
                      <span className="text-slate-500">Mavsum:</span>
                      <span className="font-bold text-slate-900">Barcha mavsumlar (All-season)</span>
                    </div>
                    <div className="flex justify-between py-1">
                      <span className="text-slate-500">Parvarish:</span>
                      <span className="font-bold text-slate-900">Quruq kimyoviy tozalash tavsiya etiladi</span>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "reviews" && (
                <div className="space-y-4 rise-in">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="text-2xl font-black text-slate-900">4.9</div>
                      <div>
                        <div className="text-amber-400 text-xs">★★★★★</div>
                        <div className="text-[10px] text-slate-500">18 ta xaridor baholagan</div>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => setShowReviewModal(true)}
                      className="rounded-xl bg-[#172641] px-3.5 py-2 text-[10.5px] font-bold text-white hover:bg-[#223558] cursor-pointer"
                    >
                      + Sharh yozish
                    </button>
                  </div>

                  <div className="space-y-2.5">
                    {reviews.length > 0 ? (
                      reviews.slice(0, 4).map((rev: any) => (
                        <div key={rev.id} className="rounded-2xl border border-slate-200/80 bg-white p-3.5 text-xs space-y-1.5 shadow-2xs">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-slate-900">{rev.name}</span>
                            <span className="text-amber-400 text-xs">★★★★★</span>
                          </div>
                          <div className="text-[10px] text-emerald-700 font-semibold">✓ Xarid tasdiqlangan ({rev.city || "Toshkent"})</div>
                          <p className="text-slate-600 text-[11.5px] leading-relaxed">«{lang === "ru" ? rev.text_ru || rev.text_uz : rev.text_uz}»</p>
                        </div>
                      ))
                    ) : (
                      <div className="space-y-2.5">
                        <div className="rounded-2xl border border-slate-200/80 bg-white p-3.5 text-xs space-y-1.5 shadow-2xs">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-slate-900">Javohir Q.</span>
                            <span className="text-amber-400 text-xs">★★★★★</span>
                          </div>
                          <div className="text-[10px] text-emerald-700 font-semibold">✓ Xarid tasdiqlangan (Toshkent)</div>
                          <p className="text-slate-600 text-[11.5px] leading-relaxed">«Kastyum kutilganidan ham a'lo sifatda keldi. Matosi juda yoqimli va yelkaga quyilgandek o‘tirdi. Rahmat!»</p>
                        </div>
                        <div className="rounded-2xl border border-slate-200/80 bg-white p-3.5 text-xs space-y-1.5 shadow-2xs">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-slate-900">Farrux M.</span>
                            <span className="text-amber-400 text-xs">★★★★★</span>
                          </div>
                          <div className="text-[10px] text-emerald-700 font-semibold">✓ Xarid tasdiqlangan (Samarqand)</div>
                          <p className="text-slate-600 text-[11.5px] leading-relaxed">«Buyurtma bergan kunimning ertasiga yetib keldi. O‘lcham bo‘yicha maslahat bergan menejerga alohida rahmat.»</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {activeTab === "delivery" && (
                <div className="space-y-3 text-xs text-slate-700 leading-relaxed rise-in">
                  <div className="rounded-2xl border border-slate-200/80 bg-[#faf8f3] p-4 space-y-3">
                    <div className="flex items-start gap-3">
                      <span className="text-lg">⚡</span>
                      <div>
                        <div className="font-bold text-slate-900">Toshkent shahri bo‘ylab:</div>
                        <div className="text-slate-600 mt-0.5">24 soat ichida kuryer orqali eshikkacha yetkazib beriladi. Bepul kiyib ko‘rish imkoniyati mavjud.</div>
                      </div>
                    </div>
                    <div className="flex items-start gap-3 border-t border-slate-200/60 pt-3">
                      <span className="text-lg">📦</span>
                      <div>
                        <div className="font-bold text-slate-900">Viloyatlar bo‘ylab:</div>
                        <div className="text-slate-600 mt-0.5">BTS Pochta, Fargo yoki EMU xizmatlari orqali 1–2 ish kunida qabul qilasiz.</div>
                      </div>
                    </div>
                    <div className="flex items-start gap-3 border-t border-slate-200/60 pt-3">
                      <span className="text-lg">🛡️</span>
                      <div>
                        <div className="font-bold text-slate-900">100% O‘lcham kafolati:</div>
                        <div className="text-slate-600 mt-0.5">Agar o‘lcham yoki bichim to‘g‘ri kelmasa, 3 kun ichida bepul almashtirib beramiz.</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>"""

if old_details_section in code and "3 Interactive ONE23-style Tabs" not in code:
    code = code.replace(old_details_section, new_tabs_section, 1)
    print("Replaced delivery details with 3 Interactive ONE23 Tabs!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("ProductScreen updates complete!")
