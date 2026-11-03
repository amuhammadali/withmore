with open(r'frontend\src\admin\AdminPages2.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# In AdminPages2.tsx, rename current broadcast-containing component to BroadcastPage,
# and write MarketingPage right below it that only contains UTM!
# Let's see what is inside MarketingPage currently:

search_str = '// ---------------- 10. MARKETING ----------------\nexport function MarketingPage() {'

broadcast_page_def = '''// ---------------- 10. TELEGRAM BROADCAST ----------------
export function BroadcastPage() {
  const { t } = useLang();
  const { toast } = useToast();

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

  return (
    <div className="space-y-6 rise-in">
      <PageHeader
        eyebrow="Marketing · Telegram"
        title="📢 Telegram Broadcast & Xabarnomalar"
        detail="Mijozlar segmentlariga moslashtirilgan rasm, tugma va havolali rasmiy Telegram xabarnomalar."
      />

      {/* Segment Selector Cards */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {[
          { id: "all", label: "Barcha mijozlar", desc: "Botdan foydalangan barcha", count: segments.all, icon: "👥" },
          { id: "vip", label: "VIP Mijozlar", desc: "LTV > 2 000 000 so'm", count: segments.vip, icon: "👑" },
          { id: "inactive_30d", label: "30+ kun kirmagan", desc: "Qaytarish (Re-activation)", count: segments.inactive_30d, icon: "💤" },
          { id: "cart_abandoned", label: "Savatni tashlab ketgan", desc: "Savatida tovar qolgan", count: segments.cart_abandoned, icon: "🛒" },
        ].map((seg) => {
          const isSel = selectedSegment === seg.id;
          return (
            <div
              key={seg.id}
              onClick={() => setSelectedSegment(seg.id)}
              className={`rounded-2xl border p-4 cursor-pointer transition-all ${
                isSel
                  ? "border-[#172641] bg-[#172641]/5 shadow-sm ring-2 ring-[#172641]/20"
                  : "border-border bg-card hover:border-[#172641]/40"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xl">{seg.icon}</span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${isSel ? "bg-[#172641] text-white" : "bg-muted text-muted-foreground"}`}>
                  {seg.count} ta mijoz
                </span>
              </div>
              <div className="mt-2 text-xs font-bold text-foreground">{seg.label}</div>
              <div className="text-[10px] text-muted-foreground mt-0.5">{seg.desc}</div>
            </div>
          );
        })}
      </div>

      {/* Main Composer & Smartphone Simulator */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12 items-start">
        {/* Left Column: Form Builder */}
        <form onSubmit={handleSendBroadcast} className="lg:col-span-7 rounded-2xl border border-border bg-card p-5 space-y-4 shadow-xs">
          <div className="border-b border-border pb-3">
            <h3 className="font-display text-base font-bold text-foreground">Yangi Telegram Kampaniyasi</h3>
            <p className="text-xs text-muted-foreground mt-0.5">Xabaringizni formatlang, rasm qo'shing va tugmani sozlang.</p>
          </div>

          <div>
            <label className="text-xs font-bold text-foreground block mb-1">Kampaniya nomi (Ichki hisobot uchun)</label>
            <input
              type="text"
              value={campTitle}
              onChange={(e) => setCampTitle(e.target.value)}
              placeholder="Masalan: Bahorgi kostyumlar chegirmasi"
              className="wm-input w-full"
              required
            />
          </div>

          <div>
            <label className="text-xs font-bold text-foreground block mb-1">Xabar matni (Markdown qo'llab-quvvatlanadi)</label>
            <textarea
              rows={5}
              value={campText}
              onChange={(e) => setCampText(e.target.value)}
              placeholder="Hurmatli mijoz! Yangi kolleksiyamiz yetib keldi..."
              className="wm-input w-full font-sans text-xs leading-relaxed"
              required
            />
          </div>

          <div>
            <label className="text-xs font-bold text-foreground block mb-1">Rasm havolasi (Ixtiyoriy)</label>
            <input
              type="url"
              value={campImage}
              onChange={(e) => setCampImage(e.target.value)}
              placeholder="https://withmore.uz/uploads/... yoki tashqi rasm URL"
              className="wm-input w-full text-xs"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-bold text-foreground block mb-1">Tugma matni</label>
              <input
                type="text"
                value={campBtnText}
                onChange={(e) => setCampBtnText(e.target.value)}
                placeholder="Kolleksiyani ko'rish 👔"
                className="wm-input w-full text-xs"
              />
            </div>
            <div>
              <label className="text-xs font-bold text-foreground block mb-1">Tugma havolasi (URL)</label>
              <input
                type="url"
                value={campBtnUrl}
                onChange={(e) => setCampBtnUrl(e.target.value)}
                placeholder="https://t.me/Withmoreuz_bot/shop"
                className="wm-input w-full text-xs"
              />
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={sendingBroadcast}
              className="w-full flex h-11 items-center justify-center gap-2 rounded-xl bg-[#172641] hover:bg-[#233555] text-xs font-bold uppercase tracking-wider text-white shadow-sm transition active:scale-[.98] cursor-pointer"
            >
              <span>📢</span>
              <span>{sendingBroadcast ? "Jo'natilmoqda..." : `${segments[selectedSegment] || 0} ta mijozga jo'natish`}</span>
            </button>
          </div>
        </form>

        {/* Right Column: Telegram Smartphone Simulator Preview */}
        <div className="lg:col-span-5 flex flex-col items-center">
          <div className="text-[11px] font-bold uppercase tracking-widest text-muted-foreground mb-2 flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>Jonli Telegram Ko'rinishi</span>
          </div>

          {/* Phone Shell */}
          <div className="w-full max-w-[320px] rounded-[36px] border-[6px] border-slate-800 bg-[#0e1621] p-3 shadow-2xl relative overflow-hidden">
            {/* Phone Notch */}
            <div className="h-4 w-28 bg-slate-800 rounded-b-xl mx-auto mb-2" />

            {/* Telegram Chat Header */}
            <div className="flex items-center gap-2 border-b border-white/10 pb-2 mb-3 px-1">
              <div className="h-7 w-7 rounded-full bg-[#c5a676] flex items-center justify-center font-bold text-[11px] text-slate-900">
                W
              </div>
              <div>
                <div className="text-xs font-bold text-white leading-none">WITHMORE</div>
                <div className="text-[9px] text-[#4ea4f6] mt-0.5">bot</div>
              </div>
            </div>

            {/* Simulated Chat Message Bubble */}
            <div className="rounded-2xl rounded-tl-sm bg-[#182533] p-3 text-[#f5f5f5] text-xs shadow-md space-y-2 border border-white/5">
              {campImage && (
                <div className="rounded-xl overflow-hidden aspect-video bg-black/40">
                  <img
                    src={campImage}
                    alt=""
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      (e.currentTarget as HTMLImageElement).style.display = 'none';
                    }}
                  />
                </div>
              )}
              <div className="whitespace-pre-wrap leading-relaxed text-[11.5px] font-normal">
                {campText || "Bu yerda siz yozgan xabarnoma matni mijozning Telegram ilovasida aynan qanday formatda ko'rinishi real vaqtda aks etadi..."}
              </div>
              <div className="text-right text-[9px] text-white/40">14:00 ✓✓</div>

              {campBtnText && (
                <div className="pt-1">
                  <div className="w-full rounded-lg bg-[#2b5278] hover:bg-[#32608d] text-center py-2 text-white text-[11px] font-semibold tracking-wide shadow-xs border border-white/10 flex items-center justify-center gap-1">
                    <span>{campBtnText}</span>
                    <span className="text-[9px] opacity-70">↗</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Broadcast History Table */}
      <div className="rounded-2xl border border-border bg-card p-5 shadow-xs space-y-3">
        <h3 className="font-display text-sm font-bold text-foreground">Yuborilgan Xabarnomalar Tarixi</h3>
        {history.length === 0 ? (
          <p className="text-xs text-muted-foreground py-2">Hali hech qanday ommaviy xabarnoma yuborilmagan.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-border text-[10px] uppercase font-bold text-muted-foreground">
                  <th className="py-2">Kampaniya</th>
                  <th className="py-2">Segment</th>
                  <th className="py-2">Qabul qiluvchilar</th>
                  <th className="py-2">Vaqt</th>
                  <th className="py-2">Holat</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {history.map((h: any) => (
                  <tr key={h.id}>
                    <td className="py-2.5 font-bold text-foreground">{h.title}</td>
                    <td className="py-2.5">
                      <span className="bg-muted px-2 py-0.5 rounded-full text-[10px] font-medium">
                        {h.segment}
                      </span>
                    </td>
                    <td className="py-2.5">{h.sent_count} ta</td>
                    <td className="py-2.5 text-muted-foreground">{new Date(h.created_at).toLocaleString("uz-UZ")}</td>
                    <td className="py-2.5 text-emerald-600 font-bold">Yuborildi ✓</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

// ---------------- 10. MARKETING & UTM ----------------
export function MarketingPage() {
'''

# In original MarketingPage:
# We just need to change activeTab default to "utm" so MarketingPage shows the UTM analytics directly!
# Or better:
old_active_tab = 'const [activeTab, setActiveTab] = useState<"broadcast" | "utm">("broadcast");'
new_active_tab = 'const [activeTab, setActiveTab] = useState<"broadcast" | "utm">("utm");'

if search_str in text:
    text = text.replace(search_str, broadcast_page_def)
    text = text.replace(old_active_tab, new_active_tab)
    print("Replaced and defined BroadcastPage + MarketingPage in AdminPages2.tsx!")
else:
    print("Could not find search_str in AdminPages2.tsx!")

with open(r'frontend\src\admin\AdminPages2.tsx', 'w', encoding='utf-8') as f:
    f.write(text)

