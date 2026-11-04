with open('frontend/src/miniapp/MiniApp.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

old_banner = '''          {/* Luxury AI Virtual Fitting Banner */}
          <div className="mt-3.5 overflow-hidden rounded-2xl border border-[#c5a676]/50 bg-gradient-to-br from-[#172641] via-[#1c2e4a] to-[#172641] p-3 sm:p-3.5 text-white shadow-md relative">
            <div className="absolute -right-6 -bottom-6 w-24 h-24 bg-[#c5a676]/15 rounded-full blur-xl pointer-events-none" />
            <div className="flex items-center justify-between gap-3 relative z-10">
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="flex h-10 w-10 sm:h-11 sm:w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-[#d6bd92] to-[#c5a676] text-slate-950 text-lg sm:text-xl shadow-xs">
                  ✨
                </div>
                <div className="min-w-0">
                  <div className="flex items-center gap-1.5">
                    <span className="text-[9px] font-bold uppercase tracking-[.18em] text-[#d6bd92] truncate">
                      AI VIRTUAL STILIST
                    </span>
                    <span className="rounded-full bg-[#c5a676]/20 border border-[#c5a676]/40 px-1.5 py-0.2 text-[8px] font-extrabold text-[#f5f1e8] shrink-0">
                      BEPUL
                    </span>
                  </div>
                  <div className="text-[12px] sm:text-[13px] font-bold text-white mt-0.5 truncate">
                    {lang === "ru" ? "Примерить на себе онлайн" : "O'zingizda kiyib ko'ring (Try-On)"}
                  </div>
                  <div className="text-[10px] sm:text-[11px] text-slate-300 truncate">
                    {lang === "ru" ? "Загрузите фото — оцените посадку костюма" : "Suratingizni yuklang — kostyum qomatingizda ko'ring"}
                  </div>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowTryOnModal(true)}
                className="shrink-0 rounded-xl bg-gradient-to-r from-[#d6bd92] to-[#c5a676] hover:brightness-105 active:scale-95 text-slate-950 text-[11px] sm:text-xs font-bold px-3 py-2 sm:px-3.5 sm:py-2.5 shadow-sm transition cursor-pointer border-0"
              >
                {lang === "ru" ? "Примерить →" : "Kiyib ko'rish →"}
              </button>
            </div>
          </div>'''

new_banner = '''          {/* Luxury AI Virtual Fitting Banner - Full Clickable Button */}
          <button
            type="button"
            onClick={() => setShowTryOnModal(true)}
            className="w-full text-left mt-3.5 overflow-hidden rounded-2xl border border-[#c5a676]/60 bg-gradient-to-br from-[#172641] via-[#1c2e4a] to-[#172641] p-3 sm:p-3.5 text-white shadow-md relative hover:shadow-xl hover:border-[#c5a676] transition-all duration-200 cursor-pointer group active:scale-[0.99] block"
          >
            <div className="absolute -right-6 -bottom-6 w-24 h-24 bg-[#c5a676]/15 rounded-full blur-xl pointer-events-none" />
            <div className="flex items-center justify-between gap-3 relative z-10">
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="flex h-10 w-10 sm:h-11 sm:w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-[#d6bd92] to-[#c5a676] text-slate-950 text-lg sm:text-xl shadow-xs group-hover:scale-105 transition-transform">
                  ✨
                </div>
                <div className="min-w-0">
                  <div className="flex items-center gap-1.5">
                    <span className="text-[9px] font-bold uppercase tracking-[.18em] text-[#d6bd92] truncate">
                      AI VIRTUAL STILIST
                    </span>
                    <span className="rounded-full bg-[#c5a676]/20 border border-[#c5a676]/40 px-1.5 py-0.2 text-[8px] font-extrabold text-[#f5f1e8] shrink-0">
                      BEPUL
                    </span>
                  </div>
                  <div className="text-[12px] sm:text-[13px] font-bold text-white mt-0.5 truncate group-hover:text-[#d6bd92] transition-colors">
                    {lang === "ru" ? "Примерить на себе онлайн" : "O'zingizda kiyib ko'ring (Try-On)"}
                  </div>
                  <div className="text-[10px] sm:text-[11px] text-slate-300 truncate">
                    {lang === "ru" ? "Boshlash uchun bu yerga bosing →" : "Boshlash uchun bu yerga bosing (Surat yuklash) →"}
                  </div>
                </div>
              </div>
              <div
                className="shrink-0 rounded-xl bg-gradient-to-r from-[#d6bd92] to-[#c5a676] group-hover:brightness-110 active:scale-95 text-slate-950 text-[11px] sm:text-xs font-bold px-3.5 py-2 sm:px-4 sm:py-2.5 shadow-sm transition flex items-center gap-1"
              >
                <span>{lang === "ru" ? "Примерить" : "Kiyib ko'rish"}</span>
                <span>→</span>
              </div>
            </div>
          </button>'''

if old_banner in code:
    code = code.replace(old_banner, new_banner, 1)
    with open('frontend/src/miniapp/MiniApp.tsx', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Banner updated to full clickable button successfully!")
else:
    print("Old banner not found exactly, check formatting")

