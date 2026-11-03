import re

# 1. Update frontend/src/admin/AdminPages2.tsx to cleanly separate BroadcastPage and MarketingPage
with open(r'frontend\src\admin\AdminPages2.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's find where MarketingPage begins
idx = text.find('export function MarketingPage()')
if idx == -1:
    print("Could not find MarketingPage in AdminPages2.tsx!")
    exit(1)

# Find the end of MarketingPage
# It ends at the end of the file or before another export
# Let's read from idx onwards
marketing_code = text[idx:]

# In marketing_code, let's extract the Broadcast logic and UTM logic
# Let's write BroadcastPage and clean MarketingPage

new_broadcast_page = '''export function BroadcastPage() {
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

export function MarketingPage() {
  const { t } = useLang();
  const { toast } = useToast();

  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);
  const [q, setQ] = useState("");
  const [utmSource, setUtmSource] = useState("instagram");
  const [utmMedium, setUtmMedium] = useState("reels");
  const [utmCampaign, setUtmCampaign] = useState("kuz_kolleksiya");
  const [botUsername, setBotUsername] = useState("Withmoreuz_bot");

  useEffect(() => {
    setLoading(true);
    adminFetch(`/api/admin/marketing?days=${days}`)
      .then(setRows)
      .finally(() => setLoading(false));
    adminFetch("/api/admin/me")
      .then((r) => {
        if (r?.bot_username) setBotUsername(r.bot_username.replace(/^@/, ""));
      })
      .catch(() => {});
  }, [days]);

  const filtered = rows.filter((r) =>
    `${r.source} ${r.medium} ${r.campaign}`
      .toLowerCase()
      .includes(q.toLowerCase())
  );

  const totals = filtered.reduce(
    (acc, r) => ({
      visits: acc.visits + (r.visits || 0),
      orders: acc.orders + (r.orders || 0),
      amount: acc.amount + (r.amount || 0),
    }),
    { visits: 0, orders: 0, amount: 0 }
  );
  const conv = totals.visits
    ? Math.round((totals.orders / totals.visits) * 100)
    : 0;

  const appUrl = (typeof window !== "undefined" ? window.location.origin : "https://withmore.uz");
  const cleanSlug = (s: string) => s.toLowerCase().replace(/[^a-z0-9_-]/g, "");

  const builtWebLink =
    utmSource.trim() && utmCampaign.trim()
      ? `${appUrl}/miniapp?utm_source=${encodeURIComponent(
          cleanSlug(utmSource)
        )}&utm_medium=${encodeURIComponent(
          cleanSlug(utmMedium || "bio")
        )}&utm_campaign=${encodeURIComponent(cleanSlug(utmCampaign))}`
      : "";

  const builtBotLink =
    utmSource.trim() && utmCampaign.trim()
      ? `https://t.me/${botUsername}?start=${cleanSlug(utmSource)}-${cleanSlug(
          utmMedium || "bio"
        )}-${cleanSlug(utmCampaign)}`
      : "";

  const copyText = (txt: string, label: string) => {
    navigator.clipboard?.writeText(txt);
    toast(`${label} nusxalandi!`);
  };

  return (
    <div className="space-y-6 rise-in">
      <PageHeader
        eyebrow="Marketing · Manbalar"
        title="📈 Reklama & UTM Trafik Tahlili"
        detail="Mini Appga qaysi havola, bloger yoki reklama orqali tashrif buyurilgani va sotuv konversiyasi."
        action={
          <div className="flex rounded-xl border border-border bg-card p-1">
            {[7, 30, 90].map((d) => (
              <button
                key={d}
                type="button"
                onClick={() => setDays(d)}
                className={`rounded-lg px-3.5 py-1.5 text-[11px] font-bold transition cursor-pointer border-0 ${
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
      />

      {/* Summary Stat Cards */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {[
          ["Tashriflar", totals.visits],
          ["Buyurtmalar", totals.orders],
          ["Konversiya", `${conv}%`],
          ["Buyurtma qiymati", formatPrice(totals.amount)],
        ].map(([lbl, val]) => (
          <div
            key={String(lbl)}
            className="rounded-2xl border border-border bg-card px-4 py-4"
          >
            <div className="text-[9px] font-bold uppercase tracking-[.14em] text-muted-foreground">
              {lbl}
            </div>
            <div className="mt-1.5 font-display text-[22px] tracking-[-.02em]">
              {val}
            </div>
          </div>
        ))}
      </div>

      {/* Link Builder */}
      <div className="rounded-2xl border border-border bg-card p-5 space-y-4 shadow-xs">
        <h3 className="font-display text-sm font-bold text-foreground">Reklama uchun kuzatuv havolalari (UTM Generator)</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div>
            <label className="wm-label">Manba (Source)</label>
            <input
              value={utmSource}
              onChange={(e) => setUtmSource(e.target.value)}
              placeholder="instagram, telegram, tiktok"
              className="wm-input w-full"
            />
          </div>
          <div>
            <label className="wm-label">Kanal turi (Medium)</label>
            <input
              value={utmMedium}
              onChange={(e) => setUtmMedium(e.target.value)}
              placeholder="reels, bio, blogger, post"
              className="wm-input w-full"
            />
          </div>
          <div>
            <label className="wm-label">Kampaniya (Campaign)</label>
            <input
              value={utmCampaign}
              onChange={(e) => setUtmCampaign(e.target.value)}
              placeholder="kuz_kolleksiya, chegirma"
              className="wm-input w-full"
            />
          </div>
        </div>

        {builtBotLink && (
          <div className="pt-2 space-y-2">
            <div className="flex items-center justify-between rounded-xl bg-muted/60 p-3">
              <div className="text-xs font-mono text-muted-foreground truncate max-w-xl">{builtBotLink}</div>
              <button
                type="button"
                onClick={() => copyText(builtBotLink, "Telegram havola")}
                className="wm-btn-secondary py-1 text-xs"
              >
                Nusxa olish
              </button>
            </div>
          </div>
        )}
      </div>

      <div>
        <label htmlFor="mk-q" className="wm-label">
          {t.search}
        </label>
        <input
          id="mk-q"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Qidiruv..."
          className="wm-input max-w-sm"
        />
      </div>

      {loading ? (
        <SkeletonList count={3} />
      ) : filtered.length === 0 ? (
        <EmptyState text="Ma'lumot topilmadi" />
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-border bg-card shadow-xs">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-border text-[10px] uppercase font-bold text-muted-foreground">
                <th className="p-3">Manba (Source)</th>
                <th className="p-3">Kanal (Medium)</th>
                <th className="p-3">Kampaniya</th>
                <th className="p-3 text-right">Tashriflar</th>
                <th className="p-3 text-right">Buyurtmalar</th>
                <th className="p-3 text-right">Konversiya</th>
                <th className="p-3 text-right">Summa</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map((r, i) => (
                <tr key={i} className="hover:bg-muted/40">
                  <td className="p-3 font-bold text-foreground">{r.source}</td>
                  <td className="p-3 text-muted-foreground">{r.medium}</td>
                  <td className="p-3">{r.campaign}</td>
                  <td className="p-3 text-right font-medium">{r.visits}</td>
                  <td className="p-3 text-right font-medium">{r.orders}</td>
                  <td className="p-3 text-right font-bold text-emerald-600">
                    {r.visits ? Math.round((r.orders / r.visits) * 100) : 0}%
                  </td>
                  <td className="p-3 text-right font-bold text-foreground">{formatPrice(r.amount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
'''

new_text = text[:idx] + new_broadcast_page
with open(r'frontend\src\admin\AdminPages2.tsx', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("AdminPages2.tsx updated: BroadcastPage and MarketingPage separated successfully!")

