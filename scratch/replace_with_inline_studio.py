with open('frontend/src/miniapp/MiniApp.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. State in ProductScreen
state_needle = 'const [showTryOnModal, setShowTryOnModal] = useState(false);'
state_replace = '''const [showTryOnModal, setShowTryOnModal] = useState(false);
  const [tryonUserPhoto, setTryonUserPhoto] = useState<string>("https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=700&q=80");
  const [tryonPresetId, setTryonPresetId] = useState<string>("m1");
  const [tryonGenerating, setTryonGenerating] = useState<boolean>(false);
  const [tryonResult, setTryonResult] = useState<string | null>(null);

  const handleTryOnFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const localUrl = URL.createObjectURL(file);
    setTryonUserPhoto(localUrl);
    setTryonPresetId("");
    setTryonResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch("/api/shop/tryon/upload", { method: "POST", body: formData });
      if (res.ok) {
        const data = await res.json();
        setTryonUserPhoto(data.url);
      }
    } catch {}
  };

  const handleInlineTryOnGenerate = async () => {
    if (!tryonUserPhoto) {
      toast("Iltimos, avval suratingizni yuklang yoki model tanlang", "error");
      return;
    }
    setTryonGenerating(true);
    try {
      const res = await shopFetch("/api/shop/tryon/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product_id: product.id,
          human_image_url: tryonUserPhoto,
          category: "upper_body"
        })
      });
      if (res.result_url) {
        setTryonResult(res.result_url);
        toast("Kiyim muvaffaqiyatli moslashtirildi!", "success");
      }
    } catch (e: any) {
      toast(e.message || "Xatolik yuz berdi", "error");
    } finally {
      setTryonGenerating(false);
    }
  };'''

if state_needle in code:
    code = code.replace(state_needle, state_replace, 1)
    print("ProductScreen state & handlers added!")
else:
    print("state_needle not found")

# 2. Replace the banner with the Inline AI Virtual Fitting Studio
banner_needle = '''          {/* Luxury AI Virtual Fitting Banner - Full Clickable Button */}
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

inline_studio = '''          {/* BESPOKE AI VIRTUAL FITTING STUDIO - INLINE LIVE STUDIO */}
          <div className="mt-4 overflow-hidden rounded-3xl border-2 border-[#c5a676]/60 bg-gradient-to-b from-[#172641] via-[#1a2d4c] to-[#121e33] p-4 text-white shadow-xl relative">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-[#d6bd92] to-[#c5a676] text-slate-950 font-bold text-lg shadow-sm">
                  ✨
                </div>
                <div>
                  <div className="text-[9px] font-bold uppercase tracking-[.2em] text-[#d6bd92]">
                    WITHMORE BESPOKE AI
                  </div>
                  <div className="font-display text-[15px] font-semibold text-white">
                    {lang === "ru" ? "Виртуальная примерка онлайн" : "Virtual Kiyib Ko'rish Studiyasi"}
                  </div>
                </div>
              </div>
              <span className="rounded-full bg-emerald-500/20 border border-emerald-400/40 px-2 py-0.5 text-[8.5px] font-extrabold text-emerald-300">
                ✓ 100% BEPUL
              </span>
            </div>

            {/* Step 1: Select or Upload Persona */}
            <div className="mt-3 space-y-2">
              <div className="text-[11px] font-medium text-slate-300 flex items-center justify-between">
                <span>{lang === "ru" ? "Загрузите фото или выберите модель:" : "Suratingizni yuklang yoki model tanlang:"}</span>
                {tryonUserPhoto && (
                  <span className="text-[9.5px] font-bold text-[#d6bd92]">✓ Tanlandi</span>
                )}
              </div>

              {/* Grid of upload + 3 models */}
              <div className="grid grid-cols-4 gap-1.5 sm:gap-2">
                {/* Upload button */}
                <label className={`flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-1 text-center cursor-pointer transition ${
                  tryonUserPhoto && !tryonPresetId ? "border-[#d6bd92] bg-white/20" : "border-white/30 hover:border-white/60 bg-white/5"
                }`}>
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handleTryOnFileUpload}
                  />
                  {tryonUserPhoto && !tryonPresetId ? (
                    <img src={tryonUserPhoto} alt="Siz" className="h-15 sm:h-16 w-full object-cover rounded-xl" />
                  ) : (
                    <div className="h-15 sm:h-16 flex flex-col items-center justify-center gap-0.5">
                      <span className="text-lg">📸</span>
                      <span className="text-[8.5px] font-bold text-slate-200 leading-tight">O'z rasm</span>
                    </div>
                  )}
                </label>

                {/* 3 Preset models */}
                {PRESET_MODELS.map((m) => (
                  <button
                    key={m.id}
                    type="button"
                    onClick={() => {
                      setTryonPresetId(m.id);
                      setTryonUserPhoto(m.photo);
                      setTryonResult(null);
                    }}
                    className={`flex flex-col items-center p-1 rounded-2xl border transition cursor-pointer text-left ${
                      tryonPresetId === m.id
                        ? "border-[#d6bd92] bg-[#d6bd92]/25 ring-2 ring-[#d6bd92]"
                        : "border-white/20 bg-white/5 hover:border-white/40"
                    }`}
                  >
                    <img src={m.photo} alt={m.name} className="h-15 sm:h-16 w-full rounded-xl object-cover" />
                    <span className="mt-1 text-[9px] font-bold text-white text-center truncate w-full">
                      {m.name}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Step 2: Generation action */}
            <div className="mt-3.5">
              {tryonGenerating ? (
                <div className="rounded-2xl border border-white/20 bg-black/50 p-4 text-center space-y-2">
                  <div className="flex items-center justify-center gap-2 text-xs font-bold text-[#d6bd92]">
                    <span className="h-2 w-2 rounded-full bg-[#d6bd92] animate-ping" />
                    <span>Mato qomatingizga moslashtirilmoqda...</span>
                  </div>
                  <div className="text-[10px] text-slate-400">
                    Withmore sartorial andazasi tikilmoqda (bir necha soniya)
                  </div>
                </div>
              ) : tryonResult ? (
                <div className="space-y-3">
                  <div className="relative aspect-[3/4] w-full max-h-[340px] overflow-hidden rounded-2xl border-2 border-[#d6bd92] shadow-xl mx-auto bg-black">
                    <img
                      src={tryonResult}
                      alt="AI Bespoke Fitting"
                      className="h-full w-full object-cover"
                    />
                    <div className="absolute top-2.5 left-2.5 rounded-full bg-slate-950/85 backdrop-blur-md px-3 py-1 text-[9px] font-extrabold text-[#d6bd92] border border-[#d6bd92]/50">
                      ✨ WITHMORE BESPOKE NATIJA
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 pt-1">
                    <button
                      type="button"
                      onClick={() => {
                        if (selectedVariant) onAddToCart(selectedVariant.id, qty);
                        else if (availableVariants[0]) onAddToCart(availableVariants[0].id, qty);
                        toast("Obraz savatga qo'shildi!", "success");
                      }}
                      className="flex h-11 items-center justify-center gap-1.5 rounded-xl bg-gradient-to-r from-[#d6bd92] to-[#c5a676] text-slate-950 text-xs font-bold uppercase tracking-wider shadow-sm transition hover:brightness-105 active:scale-95 cursor-pointer border-0"
                    >
                      <span>🛒</span>
                      <span>Savatga olish</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setTryonResult(null)}
                      className="flex h-11 items-center justify-center gap-1.5 rounded-xl border border-white/30 bg-white/10 hover:bg-white/20 text-white text-xs font-bold transition cursor-pointer"
                    >
                      <span>🔄</span>
                      <span>Qayta sinash</span>
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={handleInlineTryOnGenerate}
                  className="w-full flex h-12 items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-[#d6bd92] via-[#e5d2ae] to-[#c5a676] hover:brightness-105 active:scale-95 text-slate-950 text-xs font-black uppercase tracking-wider shadow-lg transition cursor-pointer border-0"
                >
                  <span>✨</span>
                  <span>{lang === "ru" ? "Примерить костюм на фото (AI)" : "Kiyintirib generatsiya qilish (AI Try-On)"}</span>
                </button>
              )}
            </div>
          </div>'''

if banner_needle in code:
    code = code.replace(banner_needle, inline_studio, 1)
    with open('frontend/src/miniapp/MiniApp.tsx', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Replaced banner with Inline Live Studio successfully!")
else:
    print("banner_needle not found, checking alternatives...")

