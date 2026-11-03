import os
import re

print("Starting frontend implementation for Lookbook, Referral, and Broadcast...")

# ==================== 1. MiniApp.tsx ====================
miniapp_path = "frontend/src/miniapp/MiniApp.tsx"
with open(miniapp_path, "r", encoding="utf-8") as f:
    miniapp_code = f.read()

# 1a. Add Lookbook state & fetch in HomeScreen
home_lookbook_state = '''  const [lookbooks, setLookbooks] = useState<any[]>([]);
  const [addingBundleId, setAddingBundleId] = useState<number | null>(null);

  useEffect(() => {
    shopFetch("/api/shop/lookbooks")
      .then((data) => {
        if (Array.isArray(data)) setLookbooks(data);
      })
      .catch(() => {});
  }, []);

  const handleAddBundle = async (bid: number) => {
    setAddingBundleId(bid);
    try {
      const res = await shopFetch(`/api/shop/lookbooks/${bid}/add-bundle`, {
        method: "POST",
      });
      toast(res.message || "To'liq obraz savatingizga qo'shildi!", "success");
    } catch (e: any) {
      toast(e.message || "Xatolik yuz berdi", "error");
    } finally {
      setAddingBundleId(null);
    }
  };'''

if "lookbooks, setLookbooks" not in miniapp_code:
    miniapp_code = miniapp_code.replace(
        '  const [banners, setBanners] = useState<any[]>([]);',
        '  const [banners, setBanners] = useState<any[]>([]);\n' + home_lookbook_state
    )

# 1b. Add Lookbook Carousel in HomeScreen (right under categories or brand marquee)
lookbook_section = '''      {/* ---------------- BUY THE LOOK (LOOKBOOK BUNDLES) ---------------- */}
      {lookbooks.length > 0 && (
        <section className="px-4 py-5 border-t border-[#172641]/10 bg-gradient-to-b from-[#faf8f4] to-transparent">
          <div className="flex items-center justify-between mb-3">
            <div>
              <span className="text-[9px] font-bold uppercase tracking-[.22em] text-[#a4814d] block">
                WITHMORE EDITORIAL
              </span>
              <h2 className="font-display text-[20px] font-bold text-[#172641]">
                Buy The Look · Tayyor Obrazlar
              </h2>
            </div>
            <span className="text-[10px] font-extrabold uppercase bg-[#172641] text-[#f5f1e8] px-2.5 py-1 rounded-full shadow-xs">
              -10% KOMPLEKT
            </span>
          </div>

          <div className="space-y-4">
            {lookbooks.map((look: any) => (
              <div
                key={look.id}
                className="overflow-hidden rounded-2xl border border-[#c5a676]/30 bg-white shadow-sm hover:shadow-md transition-all"
              >
                {/* Lookbook Cover & Header */}
                <div className="p-4 bg-gradient-to-r from-[#172641] to-[#25395b] text-[#f5f1e8] flex items-center justify-between">
                  <div>
                    <span className="text-[9px] font-bold uppercase tracking-[.2em] text-[#d6bd92]">
                      TAYYOR OBRAZ
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

                  {/* Included Items preview */}
                  <div className="grid grid-cols-3 gap-2 pt-1">
                    {look.items.map((it: any) => (
                      <Link
                        key={it.id}
                        to={`/miniapp/product/${it.id}`}
                        className="rounded-xl border border-slate-100 bg-[#faf8f3] p-2 text-center text-slate-900 no-underline hover:border-[#172641] transition"
                      >
                        {it.image ? (
                          <img
                            src={it.image}
                            alt=""
                            className="h-16 w-full rounded-lg object-cover mx-auto mb-1.5"
                          />
                        ) : (
                          <div className="h-16 w-full rounded-lg bg-slate-200 flex items-center justify-center text-xs mb-1.5">
                            👔
                          </div>
                        )}
                        <div className="text-[10px] font-bold truncate">
                          {lang === "ru" ? it.title_ru || it.title_uz : it.title_uz}
                        </div>
                        <div className="text-[9px] text-[#8a6c43] font-semibold mt-0.5">
                          {formatPrice(it.price)}
                        </div>
                      </Link>
                    ))}
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
        </section>
      )}
'''

if 'Kolleksiyalar va bo‘limlar' in miniapp_code and 'BUY THE LOOK (LOOKBOOK BUNDLES)' not in miniapp_code:
    # Insert Lookbook right before categories section
    pos = miniapp_code.find('{/* Editorial Luxury Category Chips Row */}')
    if pos != -1:
        miniapp_code = miniapp_code[:pos] + lookbook_section + '\n' + miniapp_code[pos:]
    else:
        print("Could not find categories position for lookbook!")

# 1c. Add Gentlemen Referral Club in AboutScreen
referral_state_code = '''  // Referral Club State
  const [refData, setRefData] = useState<any>(null);

  useEffect(() => {
    shopFetch("/api/shop/referral")
      .then(setRefData)
      .catch(() => {});
  }, []);

  const handleShareReferral = () => {
    if (!refData) return;
    const shareText = `Salom! Men Withmore premium erkaklar kiyimidan kiyinaman. Ushbu havola orqali birinchi xaridingizga 100,000 so'm sovg'a olasiz: ${refData.invite_link}`;
    const tgUrl = `https://t.me/share/url?url=${encodeURIComponent(refData.invite_link)}&text=${encodeURIComponent(shareText)}`;
    if (window.Telegram?.WebApp?.openTelegramLink) {
      window.Telegram.WebApp.openTelegramLink(tgUrl);
    } else {
      window.open(tgUrl, "_blank");
    }
    toast("Ulashish oynasi ochildi!", "success");
  };'''

if "refData, setRefData" not in miniapp_code:
    miniapp_code = miniapp_code.replace(
        '  const [openFaq, setOpenFaq] = useState<number | null>(0);',
        '  const [openFaq, setOpenFaq] = useState<number | null>(0);\n' + referral_state_code
    )

referral_ui_card = '''      {/* ---------------- GENTLEMEN REFERRAL CLUB CARD ---------------- */}
      <section className="border-t border-[#172641]/15 pt-5 space-y-3">
        <div className="rounded-2xl border-2 border-[#c5a676] bg-gradient-to-br from-[#172641] via-[#1f3357] to-[#121c2e] p-5 text-[#f5f1e8] shadow-md space-y-3.5">
          <div className="flex items-start justify-between">
            <div>
              <span className="text-[9px] font-bold uppercase tracking-[.25em] text-[#d6bd92]">
                EXCLUSIVE REFERRAL PRIVILEGE
              </span>
              <h2 className="font-display text-[22px] font-bold text-white mt-0.5">
                Gentlemen Referral Club
              </h2>
            </div>
            <span className="text-2xl">🥂</span>
          </div>

          <p className="text-xs text-[#f5f1e8]/85 leading-relaxed">
            Do‘stingizga <b>100,000 so‘m</b> xarid sovg‘asini ulashing. U birinchi buyurtmasini amalga oshirgach, sizning hisobingizga ham <b>100,000 so‘m</b> bonus tushadi!
          </p>

          <div className="grid grid-cols-2 gap-2.5 pt-1">
            <div className="rounded-xl border border-white/10 bg-white/5 p-2.5 text-center">
              <span className="text-[9px] font-bold uppercase tracking-wider text-[#d6bd92] block">
                Mening bonuslarim
              </span>
              <span className="text-base font-extrabold text-white">
                {formatPrice(refData?.bonus_balance || 0)}
              </span>
            </div>

            <div className="rounded-xl border border-white/10 bg-white/5 p-2.5 text-center">
              <span className="text-[9px] font-bold uppercase tracking-wider text-[#d6bd92] block">
                Taklif etilgan do‘stlar
              </span>
              <span className="text-base font-extrabold text-white">
                {refData?.friends_count || 0} nafar
              </span>
            </div>
          </div>

          <div className="pt-1">
            <button
              type="button"
              onClick={handleShareReferral}
              className="w-full flex h-11 items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[#c5a676] via-[#d6bd92] to-[#b38f5c] text-xs font-bold uppercase tracking-[.14em] text-[#172641] shadow-md hover:brightness-105 active:scale-[.98] transition cursor-pointer"
            >
              <span>📲</span>
              <span>Do‘stlarga Telegramdan ulashish</span>
            </button>
            <div className="mt-1.5 text-center text-[10px] text-white/60">
              Shaxsiy referal kodingiz: <b className="text-[#d6bd92]">{refData?.referral_code || "WM0001"}</b>
            </div>
          </div>
        </div>
      </section>
'''

if 'GENTLEMEN REFERRAL CLUB CARD' not in miniapp_code:
    # Insert right before `{/* Delivery & Return Rules */}`
    target_pos = miniapp_code.find('{/* Delivery & Return Rules */}')
    if target_pos != -1:
        miniapp_code = miniapp_code[:target_pos] + referral_ui_card + '\n      ' + miniapp_code[target_pos:]

with open(miniapp_path, "w", encoding="utf-8") as f:
    f.write(miniapp_code)
print("MiniApp.tsx updated with Lookbook and Referral Club!")


# ==================== 2. AdminPages2.tsx ====================
admin2_path = "frontend/src/admin/AdminPages2.tsx"
with open(admin2_path, "r", encoding="utf-8") as f:
    admin2_code = f.read()

# Add Broadcast state and tabs inside MarketingPage
marketing_search = 'export function MarketingPage() {'
marketing_code_addition = '''export function MarketingPage() {
  const { t } = useLang();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState<"broadcast" | "utm">("broadcast");

  // Broadcast state
  const [segments, setSegments] = useState<any>({ all: 0, vip: 0, inactive_30d: 0, cart_abandoned: 0 });
  const [selectedSegment, setSelectedSegment] = useState<string>("all");
  const [campTitle, setCampTitle] = useState("");
  const [campText, setCampText] = useState("");
  const [campImage, setCampImage] = useState("");
  const [campBtnText, setCampBtnText] = useState("Kolleksiyani ko'rish 👔");
  const [campBtnUrl, setCampBtnUrl] = useState("https://t.me/Withmoreuz_bot/shop");
  const [sendingBroadcast, setSendingBroadcast] = useState(false);
  const [history, setHistory] = useState<any[]>([]);

  // Load broadcast info
  const loadBroadcastData = () => {
    adminFetch("/api/admin/ops/broadcast/segments")
      .then(setSegments)
      .catch(() => {});
    adminFetch("/api/admin/ops/broadcast/history")
      .then((h) => {
        if (Array.isArray(h)) setHistory(h);
      })
      .catch(() => {});
  };

  useEffect(() => {
    loadBroadcastData();
  }, []);

  const handleSendBroadcast = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!campTitle.trim() || !campText.trim()) {
      toast("Iltimos, kampaniya nomi va xabar matnini kiriting", "error");
      return;
    }
    const count = segments[selectedSegment] || 0;
    if (!window.confirm(`Haqiqatan ham ${count} ta mijozga Telegram orqali xabarnoma jo'natmoqchimisiz?`)) {
      return;
    }

    setSendingBroadcast(true);
    try {
      const res = await adminFetch("/api/admin/ops/broadcast/send", {
        method: "POST",
        body: JSON.stringify({
          title: campTitle.trim(),
          segment: selectedSegment,
          text: campText.trim(),
          image_url: campImage.trim() || undefined,
          button_text: campBtnText.trim() || undefined,
          button_url: campBtnUrl.trim() || undefined,
        }),
      });
      toast(res.message || "Xabarnoma muvaffaqiyatli jo'natildi!", "success");
      setCampTitle("");
      setCampText("");
      setCampImage("");
      loadBroadcastData();
    } catch (e: any) {
      toast(e.message || "Xatolik yuz berdi", "error");
    } finally {
      setSendingBroadcast(false);
    }
  };
'''

if marketing_search in admin2_code and "broadcast, setBroadcast" not in admin2_code and "activeTab, setActiveTab" not in admin2_code:
    admin2_code = admin2_code.replace(marketing_search, marketing_code_addition, 1)

# Now add Broadcast UI tab and panels inside MarketingPage return
broadcast_ui_replacement = '''      <PageHeader
        eyebrow="Marketing & Growth"
        title="📢 Telegram Xabarnoma & Marketing"
        detail="Auditoriyani aqlli segmentatsiyalash, Telegram bot orqali maqsadli xabarlar yuborish va UTM tahlili."
        action={
          <div className="flex rounded-xl border border-border bg-card p-1">
            <button
              type="button"
              onClick={() => setActiveTab("broadcast")}
              className={`rounded-lg px-3.5 py-1.5 text-xs font-bold transition cursor-pointer border-0 ${
                activeTab === "broadcast"
                  ? "bg-[#172641] text-[#f5f1e8]"
                  : "bg-transparent text-muted-foreground hover:bg-muted"
              }`}
            >
              📢 Telegram Broadcast
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("utm")}
              className={`rounded-lg px-3.5 py-1.5 text-xs font-bold transition cursor-pointer border-0 ${
                activeTab === "utm"
                  ? "bg-[#172641] text-[#f5f1e8]"
                  : "bg-transparent text-muted-foreground hover:bg-muted"
              }`}
            >
              📊 UTM Manbalari
            </button>
          </div>
        }
      />

      {/* ---------------- 1. TELEGRAM SEGMENTED BROADCAST CENTER ---------------- */}
      {activeTab === "broadcast" && (
        <div className="space-y-6">
          {/* Segment Selector Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {[
              {
                key: "all",
                title: "Barcha foydalanuvchilar",
                desc: "Botga ulangan hamma mijozlar",
                count: segments.all || 0,
                icon: "👥",
              },
              {
                key: "vip",
                title: "VIP Xaridorlar",
                desc: "LTV > 2 mln so'm bo'lganlar",
                count: segments.vip || 0,
                icon: "💎",
              },
              {
                key: "inactive_30d",
                title: "Uxlab qolganlar",
                desc: "30+ kundan beri xarid qilmaganlar",
                count: segments.inactive_30d || 0,
                icon: "⏳",
              },
              {
                key: "cart_abandoned",
                title: "Savatida kiyim borlar",
                desc: "Kiyim tanlab, xarid qilmaganlar",
                count: segments.cart_abandoned || 0,
                icon: "🛒",
              },
            ].map((seg) => {
              const isSelected = selectedSegment === seg.key;
              return (
                <div
                  key={seg.key}
                  onClick={() => setSelectedSegment(seg.key)}
                  className={`rounded-2xl border p-4 cursor-pointer transition-all ${
                    isSelected
                      ? "border-[#172641] bg-[#172641] text-[#f5f1e8] shadow-md ring-2 ring-[#c5a676]"
                      : "border-border bg-card hover:border-[#172641]/50 text-foreground"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xl">{seg.icon}</span>
                    <span className={`text-xl font-display font-bold ${isSelected ? "text-[#d6bd92]" : "text-[#172641]"}`}>
                      {seg.count} ta
                    </span>
                  </div>
                  <div className="mt-2 font-bold text-xs">
                    {seg.title}
                  </div>
                  <div className={`text-[10px] mt-0.5 ${isSelected ? "text-[#f5f1e8]/75" : "text-muted-foreground"}`}>
                    {seg.desc}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Composer and Mobile Preview */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Form */}
            <div className="lg:col-span-7 rounded-2xl border border-border bg-card p-5 space-y-4 shadow-sm">
              <h2 className="text-sm font-extrabold text-[#172641] flex items-center gap-2">
                <span>✍️</span>
                <span>Yangi Telegram Xabarnoma Tuzish</span>
              </h2>

              <form onSubmit={handleSendBroadcast} className="space-y-4">
                <div>
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-muted-foreground mb-1">
                    Kampaniya nomi (Faqat admin uchun) *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="Masalan: Bahorgi VIP Kolleksiya E'loni"
                    value={campTitle}
                    onChange={(e) => setCampTitle(e.target.value)}
                    className="wm-input text-xs w-full py-2 px-3"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-muted-foreground mb-1">
                    Rasm havolasi (URL - ixtiyoriy)
                  </label>
                  <input
                    type="url"
                    placeholder="https://images.unsplash.com/... yoki rasm linki"
                    value={campImage}
                    onChange={(e) => setCampImage(e.target.value)}
                    className="wm-input text-xs w-full py-2 px-3"
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="block text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
                      Xabar matni * (Mijoz ismini qo'shish uchun: {"{name}"})
                    </label>
                    <button
                      type="button"
                      onClick={() =>
                        setCampText(
                          "Hurmatli {name}! 👔\\n\\nWithmore da cheklangan miqdordagi yangi Italiya jun matosidan tayyorlangan kostyumlar kolleksiyasi sotuvga chiqdi.\\n\\nFaqat bizning sodiq mijozlarimiz uchun maxsus taklif amal qilmoqda!"
                        )
                      }
                      className="text-[10px] text-blue-600 hover:underline"
                    >
                      + Namunaviy shablon
                    </button>
                  </div>
                  <textarea
                    rows={5}
                    required
                    placeholder="Assalomu alaykum, {name}! ..."
                    value={campText}
                    onChange={(e) => setCampText(e.target.value)}
                    className="wm-input text-xs w-full p-3 font-medium"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-1">
                      Tugma matni (ixtiyoriy)
                    </label>
                    <input
                      type="text"
                      placeholder="Kolleksiyani ko'rish 👔"
                      value={campBtnText}
                      onChange={(e) => setCampBtnText(e.target.value)}
                      className="wm-input text-xs w-full py-2 px-3"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-1">
                      Tugma havolasi (URL)
                    </label>
                    <input
                      type="text"
                      placeholder="https://t.me/Withmoreuz_bot/shop"
                      value={campBtnUrl}
                      onChange={(e) => setCampBtnUrl(e.target.value)}
                      className="wm-input text-xs w-full py-2 px-3"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={sendingBroadcast}
                  className="w-full rounded-xl bg-gradient-to-r from-[#172641] to-[#25395b] hover:from-[#223555] hover:to-[#2e4770] py-3 text-xs font-bold uppercase tracking-wider text-[#faf7f2] shadow-md transition cursor-pointer flex items-center justify-center gap-2"
                >
                  <span>🚀</span>
                  <span>
                    {sendingBroadcast
                      ? "Yuborilmoqda..."
                      : `Tanlangan auditoriyaga jo'natish (${segments[selectedSegment] || 0} ta)`}
                  </span>
                </button>
              </form>
            </div>

            {/* Live Smartphone Simulator Preview */}
            <div className="lg:col-span-5 flex flex-col items-center">
              <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground mb-2">
                📱 Telegramda qanday ko'rinadi:
              </span>
              <div className="w-[300px] rounded-3xl border-4 border-slate-800 bg-[#eef1f5] p-3 shadow-xl space-y-2">
                <div className="rounded-2xl bg-white p-3 shadow-xs space-y-2 text-xs text-slate-900">
                  {campImage && (
                    <img
                      src={campImage}
                      alt=""
                      className="w-full h-36 rounded-xl object-cover border border-slate-200"
                    />
                  )}
                  <div className="whitespace-pre-line text-[12px] leading-relaxed">
                    {campText
                      ? campText.replace("{name}", "Jasur")
                      : "Xabar matni bu yerda ko'rinadi..."}
                  </div>
                  <div className="text-[9px] text-slate-400 text-right">
                    12:45
                  </div>
                </div>

                {campBtnText && (
                  <div className="rounded-xl bg-[#2a7ed2] p-2 text-center text-xs font-bold text-white shadow-xs">
                    {campBtnText}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* History */}
          {history.length > 0 && (
            <div className="rounded-2xl border border-border bg-card overflow-hidden">
              <div className="border-b border-border bg-[#faf8f3] px-5 py-3 font-extrabold text-xs text-[#172641]">
                📋 Avval jo'natilgan xabarnomalar tarixi
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#f6f2e9] text-[9px] font-bold uppercase text-muted-foreground">
                    <tr>
                      <th className="px-5 py-2.5">Sana</th>
                      <th className="px-4 py-2.5">Kampaniya nomi</th>
                      <th className="px-4 py-2.5">Segment</th>
                      <th className="px-4 py-2.5 text-right">Yuborildi</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/60">
                    {history.map((h: any) => (
                      <tr key={h.id}>
                        <td className="px-5 py-2.5 text-muted-foreground">{h.created_at}</td>
                        <td className="px-4 py-2.5 font-bold text-foreground">{h.title}</td>
                        <td className="px-4 py-2.5 uppercase text-[10px] font-bold text-[#8a6c43]">
                          {h.segment}
                        </td>
                        <td className="px-4 py-2.5 text-right font-extrabold text-[#172641]">
                          {h.sent_count} ta
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ---------------- 2. UTM SOURCES VIEW ---------------- */}
      {activeTab === "utm" && (
'''

# Replace PageHeader in MarketingPage
old_header_target = '''      <PageHeader
        eyebrow={t.marketing}
        title={t.utmStats}
        detail="Qaysi reklama kanallari (Instagram, Telegram kanal, blogerlar) ko'proq mijoz va buyurtma olib kelayotganini tahlil qiling."
        action={
          <div className="flex rounded-xl border border-border bg-card p-1">
            {[7, 30, 90].map((d) => (
              <button
                key={d}
                type="button"
                onClick={() => setDays(d)}
                className={`rounded-lg px-3.5 py-1.5 text-xs font-bold transition cursor-pointer border-0 ${
                  days === d
                    ? "bg-[#172641] text-[#f5f1e8]"
                    : "bg-transparent text-muted-foreground hover:bg-muted"
                }`}
              >
                {d} kun
              </button>
            ))}
          </div>
        }
      />'''

if old_header_target in admin2_code and "Telegram Xabarnoma & Marketing" not in admin2_code:
    admin2_code = admin2_code.replace(old_header_target, broadcast_ui_replacement)
    # close the activeTab === 'utm' conditional at the end of the page
    # find the end of MarketingPage
    end_marketing = '    </div>\n  );\n}\n\nexport function GrowthPage() {'
    if end_marketing in admin2_code:
        admin2_code = admin2_code.replace(
            end_marketing,
            '      )}\n    </div>\n  );\n}\n\nexport function GrowthPage() {'
        )

with open(admin2_path, "w", encoding="utf-8") as f:
    f.write(admin2_code)
print("AdminPages2.tsx updated with Telegram Broadcast Center!")

