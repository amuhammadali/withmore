import re

with open('frontend/src/miniapp/MiniApp.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Component definition for AIVirtualFittingModal
modal_component = '''
// ---------------- CREATIVE AI VIRTUAL FITTING ROOM MODAL ----------------
const PRESET_MODELS = [
  {
    id: "m1",
    name: "Klassik bo'y",
    desc: "180 sm · 78 kg",
    photo: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=700&q=80"
  },
  {
    id: "m2",
    name: "Atletik qomat",
    desc: "185 sm · 84 kg",
    photo: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=700&q=80"
  },
  {
    id: "m3",
    name: "Slim Fit",
    desc: "176 sm · 70 kg",
    photo: "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?auto=format&fit=crop&w=700&q=80"
  }
];

function AIVirtualFittingModal({
  product,
  onClose,
  onAddToCart,
}: {
  product: any;
  onClose: () => void;
  onAddToCart: () => void;
}) {
  const { lang } = useLang();
  const [tab, setTab] = useState<"upload" | "presets">("upload");
  const [selectedPhoto, setSelectedPhoto] = useState<string>("");
  const [uploadedFileUrl, setUploadedFileUrl] = useState<string>("");
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [statusIdx, setStatusIdx] = useState<number>(0);
  const [resultUrl, setResultUrl] = useState<string>("");
  const [viewMode, setViewMode] = useState<"after" | "before">("after");
  const [errorMsg, setErrorMsg] = useState<string>("");

  const statusTexts = [
    lang === "ru" ? "Анализируем пропорции тела..." : "Mato qomatingizga moslashtirilmoqda...",
    lang === "ru" ? "Подгоняем лекала Withmore..." : "Yelka va yoqa chiziqlari Withmore andazasida tikilmoqda...",
    lang === "ru" ? "Гармонизируем освещение и ткань..." : "Mavsumiy yorug'lik va teksturalar uyg'unlashtirilmoqda...",
    lang === "ru" ? "Финализируем ваш премиальный образ..." : "Yakuniy ko'rinish tayyorlanmoqda...",
  ];

  useEffect(() => {
    let timer: any;
    if (isGenerating) {
      timer = setInterval(() => {
        setStatusIdx((prev) => (prev + 1) % statusTexts.length);
      }, 2500);
    }
    return () => clearInterval(timer);
  }, [isGenerating]);

  // Set default photo to first preset if none selected
  useEffect(() => {
    if (!selectedPhoto && PRESET_MODELS[0]) {
      setSelectedPhoto(PRESET_MODELS[0].photo);
    }
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Local preview immediately
    const localUrl = URL.createObjectURL(file);
    setSelectedPhoto(localUrl);
    setResultUrl("");
    setErrorMsg("");
    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("/api/shop/tryon/upload", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Rasmni yuklashda xatolik yuz berdi");
      const data = await res.json();
      setUploadedFileUrl(data.url);
      setSelectedPhoto(data.url);
    } catch (err: any) {
      setErrorMsg(err.message || "Rasmni yuklab bo'lmadi");
    } finally {
      setIsUploading(false);
    }
  };

  const handleStartTryOn = async () => {
    const photoToUse = uploadedFileUrl || selectedPhoto;
    if (!photoToUse) {
      setErrorMsg("Iltimos, avval suratingizni yuklang yoki namunani tanlang");
      return;
    }

    setIsGenerating(true);
    setErrorMsg("");
    setStatusIdx(0);

    try {
      const res = await shopFetch("/api/shop/tryon/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product_id: product.id,
          human_image_url: photoToUse,
          category: "upper_body",
        }),
      });

      if (res.result_url) {
        setResultUrl(res.result_url);
        setViewMode("after");
      } else {
        throw new Error(res.message || "Generatsiyada kutilmagan holat yuz berdi");
      }
    } catch (err: any) {
      setErrorMsg(err.message || "AI servisi bilan ulanishda xatolik yuz berdi");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleShare = () => {
    const title = `Withmore Bespoke: ${product.name_uz}`;
    const text = `Men Withmore'dan ushbu kiyimni o'zimda kiyib ko'rdim. Qanday turibdi?`;
    const shareUrl = window.location.href;

    if (navigator.share) {
      navigator.share({ title, text, url: shareUrl }).catch(() => {});
    } else {
      window.open(
        `https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(text)}`,
        "_blank"
      );
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/75 backdrop-blur-sm p-0 sm:p-4 animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg rounded-t-3xl sm:rounded-3xl border border-[#c5a676]/40 bg-white p-5 shadow-2xl max-h-[92vh] overflow-y-auto no-scrollbar relative flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Atelier Header */}
        <div className="flex items-start justify-between border-b border-slate-100 pb-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[9px] font-bold uppercase tracking-[.22em] text-[#a4814d] block">
                WITHMORE ATELIER
              </span>
              <span className="rounded-full bg-[#172641] text-[#d6bd92] px-2 py-0.2 text-[8px] font-extrabold tracking-wider">
                ✨ AI VIRTUAL FITTING
              </span>
            </div>
            <h3 className="font-display text-[18px] sm:text-[20px] font-semibold text-slate-900 mt-0.5">
              {lang === "ru" ? "Виртуальная примерка" : "O'zingizda kiyib ko'rish"}
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-100 text-slate-500 hover:bg-slate-200 text-sm font-bold border-0 cursor-pointer"
          >
            ✕
          </button>
        </div>

        {/* Product mini bar */}
        <div className="mt-3 flex items-center justify-between gap-3 rounded-2xl bg-[#faf8f4] border border-[#d6bd92]/30 p-2.5">
          <div className="flex items-center gap-2.5 min-w-0">
            {product.images && product.images[0] ? (
              <ProductImage
                src={product.images[0]}
                alt=""
                className="h-11 w-9 rounded-lg object-cover shrink-0"
              />
            ) : null}
            <div className="min-w-0">
              <div className="text-xs font-bold text-slate-900 truncate">
                {product.name_uz}
              </div>
              <div className="text-[11px] font-bold text-[#8a6c43]">
                {formatPrice(product.price)}
              </div>
            </div>
          </div>
          <span className="text-[9px] font-bold uppercase tracking-wider text-emerald-800 bg-emerald-100 px-2 py-1 rounded-full shrink-0">
            ✓ 100% BEPUL
          </span>
        </div>

        {/* Content Body */}
        {!resultUrl && !isGenerating ? (
          <div className="mt-4 space-y-4">
            {/* Tabs: Upload vs Presets */}
            <div className="grid grid-cols-2 gap-1 rounded-xl bg-slate-100 p-1">
              <button
                type="button"
                onClick={() => setTab("upload")}
                className={`py-2 text-xs font-bold rounded-lg transition cursor-pointer border-0 ${
                  tab === "upload"
                    ? "bg-white text-slate-900 shadow-xs"
                    : "text-slate-500 hover:text-slate-900"
                }`}
              >
                📸 O'z suratingiz
              </button>
              <button
                type="button"
                onClick={() => setTab("presets")}
                className={`py-2 text-xs font-bold rounded-lg transition cursor-pointer border-0 ${
                  tab === "presets"
                    ? "bg-white text-slate-900 shadow-xs"
                    : "text-slate-500 hover:text-slate-900"
                }`}
              >
                👤 Namuna modellar
              </button>
            </div>

            {tab === "upload" ? (
              <div className="space-y-3">
                <label className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-[#c5a676]/60 bg-[#faf8f3] p-5 text-center cursor-pointer hover:border-[#172641] transition group">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                  {selectedPhoto && uploadedFileUrl ? (
                    <div className="relative aspect-[3/4] w-36 overflow-hidden rounded-xl border border-slate-200 shadow-xs">
                      <img
                        src={selectedPhoto}
                        alt="Tanlangan rasm"
                        className="h-full w-full object-cover"
                      />
                      <span className="absolute bottom-1 inset-x-1 rounded-md bg-black/60 text-[9px] font-bold text-white py-1">
                        Rasmni almashtirish
                      </span>
                    </div>
                  ) : (
                    <>
                      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#172641] text-white text-xl shadow-xs group-hover:scale-105 transition">
                        📸
                      </div>
                      <span className="mt-2 text-xs font-bold text-slate-900">
                        {isUploading ? "Rasm yuklanmoqda..." : "Suratingizni yuklang"}
                      </span>
                      <span className="mt-1 text-[10px] text-slate-500 max-w-[240px]">
                        To'liq bo'y yoki beligacha tushgan, yorug' surat eng yaxshi natija beradi
                      </span>
                    </>
                  )}
                </label>
              </div>
            ) : (
              <div className="space-y-2">
                <span className="text-[11px] font-semibold text-slate-600">
                  O'zingizga yaqin tana tuzilishini tanlang:
                </span>
                <div className="grid grid-cols-3 gap-2">
                  {PRESET_MODELS.map((m) => (
                    <button
                      key={m.id}
                      type="button"
                      onClick={() => {
                        setSelectedPhoto(m.photo);
                        setUploadedFileUrl("");
                      }}
                      className={`flex flex-col items-center p-2 rounded-2xl border transition cursor-pointer text-left ${
                        selectedPhoto === m.photo
                          ? "border-[#172641] bg-[#172641]/5 ring-2 ring-[#172641]"
                          : "border-slate-200 hover:border-slate-300 bg-white"
                      }`}
                    >
                      <img
                        src={m.photo}
                        alt={m.name}
                        className="h-20 w-full rounded-xl object-cover"
                      />
                      <span className="mt-1.5 text-[11px] font-bold text-slate-900 truncate w-full text-center">
                        {m.name}
                      </span>
                      <span className="text-[9px] text-slate-500 text-center">
                        {m.desc}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {errorMsg && (
              <div className="rounded-xl bg-rose-50 border border-rose-200 p-2.5 text-xs text-rose-700">
                {errorMsg}
              </div>
            )}

            {/* Launch Button */}
            <button
              type="button"
              disabled={isUploading}
              onClick={handleStartTryOn}
              className="w-full flex h-12 items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-[#172641] to-[#25395b] hover:brightness-105 active:scale-95 text-[#f5f1e8] text-xs font-bold uppercase tracking-wider shadow-md transition cursor-pointer border-0 mt-2"
            >
              <span>✨</span>
              <span>Kiyib ko'rishni boshlash (AI Try-On)</span>
            </button>
          </div>
        ) : isGenerating ? (
          /* Tailoring In Progress Animation */
          <div className="my-8 flex flex-col items-center justify-center text-center space-y-4">
            <div className="relative aspect-[3/4] w-48 overflow-hidden rounded-2xl border-2 border-[#c5a676] bg-slate-950 shadow-2xl">
              {selectedPhoto && (
                <img
                  src={selectedPhoto}
                  alt="Scanning"
                  className="h-full w-full object-cover opacity-70"
                />
              )}
              {/* Laser scanning bar */}
              <div className="absolute inset-x-0 h-1.5 bg-gradient-to-r from-transparent via-[#c5a676] to-transparent shadow-[0_0_15px_#c5a676] animate-pulse"
                style={{
                  top: "40%",
                  animation: "bounce 2s infinite"
                }}
              />
              <div className="absolute bottom-2 inset-x-2 rounded-lg bg-black/70 backdrop-blur-xs py-1 text-[9px] font-bold text-[#f5f1e8]">
                Withmore Bespoke Fitting...
              </div>
            </div>

            <div className="space-y-1">
              <div className="flex items-center justify-center gap-2 text-xs font-bold text-slate-900">
                <span className="inline-block h-2 w-2 rounded-full bg-[#c5a676] animate-ping" />
                <span>{statusTexts[statusIdx]}</span>
              </div>
              <p className="text-[10px] text-slate-400">
                Bu jarayon bir necha soniya vaqt oladi
              </p>
            </div>
          </div>
        ) : (
          /* Result Showcase */
          <div className="mt-4 space-y-4">
            {/* View Mode Toggle */}
            <div className="flex items-center justify-center gap-1">
              <div className="inline-flex rounded-xl bg-slate-100 p-1">
                <button
                  type="button"
                  onClick={() => setViewMode("after")}
                  className={`px-3 py-1 text-xs font-bold rounded-lg transition cursor-pointer border-0 ${
                    viewMode === "after"
                      ? "bg-[#172641] text-white shadow-xs"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  👔 Withmore kiyimida
                </button>
                <button
                  type="button"
                  onClick={() => setViewMode("before")}
                  className={`px-3 py-1 text-xs font-bold rounded-lg transition cursor-pointer border-0 ${
                    viewMode === "before"
                      ? "bg-white text-slate-900 shadow-xs"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  👁️ Asl surat
                </button>
              </div>
            </div>

            {/* Display Image */}
            <div className="relative aspect-[3/4] w-full max-h-[380px] overflow-hidden rounded-2xl border border-slate-200 bg-slate-900 shadow-md mx-auto">
              <img
                src={viewMode === "after" ? resultUrl : selectedPhoto}
                alt="Fitting Result"
                className="h-full w-full object-cover transition-all duration-300"
              />
              <div className="absolute top-2.5 left-2.5 rounded-full bg-slate-950/70 backdrop-blur-md px-2.5 py-0.5 text-[9px] font-bold text-white border border-white/20">
                {viewMode === "after" ? "✨ Withmore Sartorial Cut" : "Asl surat"}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="space-y-2 pt-1">
              <button
                type="button"
                onClick={() => {
                  onAddToCart();
                  onClose();
                }}
                className="w-full flex h-12 items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-[#d6bd92] to-[#c5a676] hover:brightness-105 active:scale-95 text-slate-950 text-xs font-bold uppercase tracking-wider shadow-md transition cursor-pointer border-0"
              >
                <span>🛒</span>
                <span>Ushbu obrazni savatga qo'shish</span>
              </button>

              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={handleShare}
                  className="flex h-10 items-center justify-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-800 text-xs font-semibold transition cursor-pointer"
                >
                  <span>📲</span>
                  <span>Ulashish</span>
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setResultUrl("");
                    setErrorMsg("");
                  }}
                  className="flex h-10 items-center justify-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-800 text-xs font-semibold transition cursor-pointer"
                >
                  <span>🔄</span>
                  <span>Boshqa rasm</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
'''

# Check if AIVirtualFittingModal already exists
if "AIVirtualFittingModal" not in code:
    # Insert right before ProductScreen
    target = "function ProductScreen({"
    if target in code:
        code = code.replace(target, modal_component + "\n\n" + target, 1)
        print("AIVirtualFittingModal inserted before ProductScreen!")
    else:
        print("Error: Could not find ProductScreen declaration")
else:
    print("AIVirtualFittingModal already exists in MiniApp.tsx")

# 2. Add showTryOnModal state to ProductScreen
state_target = 'const [showSizeCalc, setShowSizeCalc] = useState(false);'
state_replacement = '''const [showSizeCalc, setShowSizeCalc] = useState(false);
  const [showTryOnModal, setShowTryOnModal] = useState(false);'''

if state_target in code and "showTryOnModal" not in code:
    code = code.replace(state_target, state_replacement, 1)
    print("showTryOnModal state added to ProductScreen!")

# 3. Add AI Fitting Banner into ProductScreen (after Stock Scarcity Status)
banner_target = '{/* Stock Scarcity Status */}'
banner_code = '''{/* Stock Scarcity Status */}

          {/* Luxury AI Virtual Fitting Banner */}
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

if banner_target in code and "AI VIRTUAL STILIST" not in code:
    code = code.replace(banner_target, banner_code, 1)
    print("AI Fitting Banner inserted into ProductScreen!")

# 4. Add Modal Render at the end of ProductScreen
modal_render_target = '{/* Size Chart Modal */}'
modal_render_code = '''{/* AI Virtual Fitting Modal */}
      {showTryOnModal && (
        <AIVirtualFittingModal
          product={product}
          onClose={() => setShowTryOnModal(false)}
          onAddToCart={() => {
            if (selectedVariant) {
              onAddToCart(selectedVariant.id, qty);
              toast(t.addedToCart, "success");
            } else if (availableVariants[0]) {
              onAddToCart(availableVariants[0].id, qty);
              toast(t.addedToCart, "success");
            }
          }}
        />
      )}

      {/* Size Chart Modal */}'''

if modal_render_target in code and "AIVirtualFittingModal" in code and "showTryOnModal &&" not in code:
    code = code.replace(modal_render_target, modal_render_code, 1)
    print("AIVirtualFittingModal render wired at the end of ProductScreen!")

with open('frontend/src/miniapp/MiniApp.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated MiniApp.tsx successfully!")

