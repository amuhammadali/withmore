import React, { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { adminFetch } from "../api";
import { calcSellingPrice, formatPrice, STATUS_LABELS, useLang } from "../i18n";
import {
  ConfirmModal,
  EmptyState,
  SkeletonList,
  StatusBadge,
  useToast,
} from "../ui";
export {
  AuditPage,
  ContentPage,
  CustomersPage,
  GrowthPage,
  MarketingPage,
  OrderDetailPage,
  OrdersPage,
  PromotionsPage,
  SettingsPage,
  TeamPage,
} from "./AdminPages2";

export function PageHeader({
  eyebrow,
  title,
  detail,
  action,
}: {
  eyebrow: string;
  title: string;
  detail?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="mb-7 flex flex-wrap items-end justify-between gap-4 rise-in">
      <div>
        <div className="mb-2 text-[9px] font-bold uppercase tracking-[.2em] text-[#aa8a5e]">
          {eyebrow}
        </div>
        <h1 className="font-display text-[28px] font-medium tracking-[-.035em] md:text-[36px]">
          {title}
        </h1>
        {detail && (
          <p className="mt-1.5 text-[12px] text-muted-foreground">{detail}</p>
        )}
      </div>
      {action}
    </div>
  );
}

// ---------------- 1. DASHBOARD ----------------
export function DashboardPage({ adminName }: { adminName?: string }) {
  const { t } = useLang();
  const { toast } = useToast();
  const [days, setDays] = useState(30);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    adminFetch(`/api/admin/dashboard?days=${days}`)
      .then(setData)
      .catch((e) => toast(e.message, "error"))
      .finally(() => setLoading(false));
  }, [days]);

  if (loading || !data) return <SkeletonList count={6} />;

  const c = data.cards;
  const series: { date: string; orders: number; visits: number }[] =
    data.series || [];
  const maxVal = Math.max(
    1,
    ...series.map((s) => Math.max(s.orders, s.visits))
  );

  const width = 600;
  const height = 160;
  const pts = (key: "orders" | "visits") =>
    series
      .map((s, idx) => {
        const x =
          series.length > 1
            ? (idx / (series.length - 1)) * (width - 20) + 10
            : width / 2;
        const y = height - 15 - (s[key] / maxVal) * (height - 30);
        return `${x},${y}`;
      })
      .join(" ");

  const funnelLabels: Record<string, string> = {
    viewed: t.funnelViewed,
    cart: t.funnelCart,
    contact: t.funnelContact,
    order: t.funnelOrder,
  };
  const funnelMax = Math.max(
    1,
    ...(data.funnel || []).map((f: any) => f.value)
  );

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow={`Ish stoli · ${t.dashboard}`}
        title={`Xayrli kun${adminName ? `, ${adminName}` : ""}.`}
        detail={`Oxirgi ${days} kundagi do‘kon ko‘rsatkichlari va buyurtmalar oqimi.`}
        action={
          <div
            className="flex rounded-xl border border-border bg-card p-1"
            role="group"
            aria-label="Davr"
          >
            {[
              { d: 7, l: t.period7 },
              { d: 30, l: t.period30 },
              { d: 90, l: t.period90 },
              { d: 365, l: t.period365 },
            ].map((p) => (
              <button
                key={p.d}
                type="button"
                onClick={() => setDays(p.d)}
                className={`rounded-lg px-3.5 py-1.5 text-[11px] font-bold transition cursor-pointer border-0 ${
                  days === p.d
                    ? "bg-[#172641] text-[#f5f1e8]"
                    : "bg-transparent text-muted-foreground hover:bg-muted"
                }`}
              >
                {p.l}
              </button>
            ))}
          </div>
        }
      />

      {/* 3 Primary Tone Cards (Navy, Sand, Sage) */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <ToneCard
          tone="navy"
          label={t.cardOrderedAmount}
          value={formatPrice(c.ordered_amount)}
          sub={`Jami buyurtmalar: ${c.orders} ta · bekor: ${c.cancelled}`}
        />
        <ToneCard
          tone="sand"
          label={t.cardPaidAmount}
          value={formatPrice(c.paid_amount)}
          sub="Tasdiqlangan to‘lovlar summasi"
        />
        <ToneCard
          tone="sage"
          label={t.cardDelivered}
          value={`${c.delivered} ta`}
          sub="Mijozga topshirilgan buyurtmalar"
        />
      </div>

      {/* 6 Secondary Metric Cards */}
      <div className="grid grid-cols-2 gap-3.5 lg:grid-cols-6">
        <MetricCard
          label={t.cardVisits}
          value={c.visits}
          sub={`${days} kun`}
          tone="blue"
          icon="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3"
        />
        <MetricCard
          label={t.cardViews}
          value={c.views}
          sub="Mahsulot sahifasi"
          tone="sand"
          icon="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"
        />
        <MetricCard
          label={t.cardContacts}
          value={c.contacts}
          sub="Telegram tugmasi"
          tone="rose"
          icon="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"
        />
        <MetricCard
          label={t.cardConversion}
          value={`${c.conversion}%`}
          sub="Buyurtma / tashrif"
          tone="mint"
          icon="M23 6l-9.5 9.5-5-5L1 18M17 6h6v6"
        />
        <MetricCard
          label={t.cardCustomers}
          value={c.customers}
          sub="Ro‘yxatdan o‘tgan"
          tone="blue"
          icon="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z"
        />
        <MetricCard
          label={t.cardOrders}
          value={c.orders}
          sub={`Bekor: ${c.cancelled}`}
          tone="sand"
          icon="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"
        />
      </div>

      {/* Recent Orders & Top Products (Replit 2-column layout) */}
      <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1.28fr_.72fr]">
        <section className="rounded-2xl border border-border bg-card p-6">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-[15px] font-extrabold">{t.latestOrders}</h2>
              <p className="text-[11px] text-muted-foreground">
                Oxirgi kelib tushgan so‘rovlar
              </p>
            </div>
            <Link
              to="/admin/orders"
              className="inline-flex items-center gap-1 text-[11px] font-bold text-primary no-underline hover:underline"
            >
              Barchasini ko‘rish →
            </Link>
          </div>
          {(data.latest_orders || []).length === 0 ? (
            <EmptyState text="Hozircha buyurtmalar yo‘q." />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[520px] text-left text-xs">
                <thead className="border-b border-border text-[9px] font-bold uppercase tracking-[.12em] text-muted-foreground">
                  <tr>
                    <th className="py-2.5">Buyurtma</th>
                    <th className="py-2.5">Mijoz</th>
                    <th className="py-2.5">Holat</th>
                    <th className="py-2.5 text-right">Jami</th>
                  </tr>
                </thead>
                <tbody>
                  {data.latest_orders.map((o: any) => (
                    <tr
                      key={o.id}
                      className="border-b border-border/60 last:border-0 hover:bg-[#f9f6ef]"
                    >
                      <td className="py-3 font-extrabold">
                        <Link
                          to={`/admin/orders/${o.id}`}
                          className="text-foreground no-underline hover:underline"
                        >
                          {o.code}
                        </Link>
                      </td>
                      <td className="py-3 font-semibold">{o.name}</td>
                      <td className="py-3">
                        <StatusBadge status={o.status} />
                      </td>
                      <td className="py-3 text-right font-extrabold">
                        {formatPrice(o.total)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <section className="rounded-2xl border border-border bg-card p-6">
          <h2 className="text-[15px] font-extrabold">{t.topProducts}</h2>
          <p className="mb-4 text-[11px] text-muted-foreground">
            Tanlangan davrdagi faol buyurtmalar bo‘yicha
          </p>
          {(data.top_products || []).length === 0 ? (
            <EmptyState text="Tanlangan davrda buyurtmalar yo‘q." />
          ) : (
            <div className="space-y-3">
              {data.top_products.map((p: any, i: number) => (
                <div
                  key={i}
                  className="flex items-center gap-3 rounded-xl border border-border/70 bg-[#faf8f3] p-2.5"
                >
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#172641] font-display text-sm font-semibold text-[#d6bd92]">
                    #{i + 1}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-[12px] font-bold">
                      {p.name}
                    </div>
                    <div className="text-[10px] text-muted-foreground">
                      {p.qty} dona sotilgan
                    </div>
                  </div>
                  <div className="text-right text-[11px] font-extrabold">
                    {formatPrice(p.amount)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      {/* Daily Line Chart & Conversion Funnel */}
      <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
        <section className="rounded-2xl border border-border bg-card p-6 space-y-4 shadow-xs">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-[10px] font-bold uppercase tracking-[.16em] text-[#8d6e43]">
                Analitika Dinamikasi
              </div>
              <h2 className="text-[16px] font-extrabold text-[#172641]">
                {t.dailyChart}
              </h2>
              <p className="text-[11px] text-muted-foreground">
                Kunlik tashriflar va buyurtmalar dinamikasi
              </p>
            </div>
            <div className="flex items-center gap-3 text-[11px] font-semibold bg-[#faf8f3] px-3 py-1.5 rounded-xl border border-border/70">
              <span className="inline-flex items-center gap-1.5 text-[#172641]">
                <span className="h-2 w-2 rounded-full bg-[#172641]" />
                {t.cardVisits}
              </span>
              <span className="inline-flex items-center gap-1.5 text-[#8d6e43]">
                <span className="h-2 w-2 rounded-full bg-[#c5a776]" />
                {t.cardOrders}
              </span>
            </div>
          </div>
          <div className="relative overflow-hidden rounded-xl border border-border/70 bg-gradient-to-b from-[#faf8f3] to-[#f4ede1]/40 p-2">
            <svg
              viewBox={`0 0 ${width} ${height}`}
              className="w-full h-44 drop-shadow-xs"
            >
              <defs>
                <linearGradient id="adminChartGlow" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#c5a776" stopOpacity="0.3" />
                  <stop offset="100%" stopColor="#c5a776" stopOpacity="0.0" />
                </linearGradient>
              </defs>
              <polyline
                fill="none"
                stroke="#172641"
                strokeWidth="2"
                strokeDasharray="4 4"
                opacity="0.45"
                points={pts("visits")}
              />
              <polyline
                fill="none"
                stroke="#c5a776"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
                points={pts("orders")}
              />
            </svg>
          </div>
        </section>

        <section className="rounded-2xl border border-border bg-card p-6 space-y-4 shadow-xs">
          <div>
            <div className="text-[10px] font-bold uppercase tracking-[.16em] text-[#8d6e43]">
              Konversiya Voronkasi
            </div>
            <h2 className="text-[16px] font-extrabold text-[#172641]">
              {t.funnelTitle}
            </h2>
            <p className="text-[11px] text-muted-foreground">
              Ko‘rishdan to‘lov va topshirishgacha bo‘lgan konversiya
            </p>
          </div>
          <div className="space-y-3.5 pt-1">
            {(data.funnel || []).map((f: any) => {
              const pct = funnelMax > 0 ? Math.round((f.value / funnelMax) * 100) : 0;
              return (
                <div key={f.key} className="space-y-1.5">
                  <div className="flex justify-between text-xs font-bold">
                    <span className="text-[#172641]">
                      {funnelLabels[f.key] || f.key}
                    </span>
                    <span className="flex items-center gap-2">
                      <span className="text-[10px] text-muted-foreground font-medium">{pct}%</span>
                      <span className="rounded-md bg-[#172641]/10 px-1.5 py-0.5 text-[11px] text-[#172641]">
                        {f.value}
                      </span>
                    </span>
                  </div>
                  <div className="h-3 rounded-full bg-[#f1ebd9] overflow-hidden p-0.5 border border-[#e4d7bf]/50">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-[#172641] via-[#243c68] to-[#c5a776] transition-all duration-700"
                      style={{
                        width: `${Math.max(5, (f.value / funnelMax) * 100)}%`,
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      </div>

      {/* Needs Attention */}
      <section className="rounded-2xl border border-border bg-card p-6 space-y-3 shadow-xs">
        <h2 className="text-[15px] font-extrabold">{t.needsAttention}</h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div className="rounded-xl border border-border/80 bg-[#faf8f3] p-4">
            <div className="text-xs font-extrabold mb-2">
              {t.waitingPayment} ({data.attention?.awaiting_payment?.length || 0}
              )
            </div>
            {(data.attention?.awaiting_payment || []).length === 0 ? (
              <div className="text-xs text-muted-foreground">Yo‘q</div>
            ) : (
              <div className="space-y-1.5">
                {data.attention.awaiting_payment.map((o: any) => (
                  <Link
                    key={o.id}
                    to={`/admin/orders/${o.id}`}
                    className="flex justify-between text-xs font-semibold text-[#172641] no-underline hover:underline"
                  >
                    <span>
                      {o.code} — {o.name}
                    </span>
                    <span>{formatPrice(o.total)}</span>
                  </Link>
                ))}
              </div>
            )}
          </div>
          <div className="rounded-xl border border-border/80 bg-[#faf8f3] p-4">
            <div className="text-xs font-extrabold mb-2">
              {t.failedNotifications} ({data.attention?.failed_messages || 0})
            </div>
            {(data.attention?.failed_orders || []).length === 0 ? (
              <div className="text-xs text-muted-foreground">Yo‘q</div>
            ) : (
              <div className="space-y-1.5">
                {data.attention.failed_orders.map((o: any) => (
                  <Link
                    key={o.id}
                    to={`/admin/orders/${o.id}`}
                    className="block text-xs font-semibold text-[#a3463c] no-underline hover:underline"
                  >
                    {o.code} — {o.name}
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}

function ToneCard({
  tone,
  label,
  value,
  sub,
}: {
  tone: "navy" | "sand" | "sage";
  label: string;
  value: string;
  sub: string;
}) {
  const styles = {
    navy: "bg-gradient-to-br from-[#172641] via-[#1a2d4f] to-[#101b2f] text-[#f5f1e8] border border-[#2b4169]/50 shadow-lg shadow-[#172641]/15",
    sand: "bg-gradient-to-br from-[#faf4e8] via-[#f3e7d1] to-[#e8d5b5] text-[#172641] border border-[#dfcaa1] shadow-sm",
    sage: "bg-gradient-to-br from-[#f2f8f3] via-[#e2efe3] to-[#cbe2cd] text-[#193a23] border border-[#b8dab9] shadow-sm",
  }[tone];

  const pillStyles = {
    navy: "bg-white/10 text-[#d6bd92] border border-white/15",
    sand: "bg-white/70 text-[#8a6c43] border border-[#d6bd92]/50",
    sage: "bg-white/70 text-[#285736] border border-[#9dcf9f]/50",
  }[tone];

  return (
    <div
      className={`group relative overflow-hidden rounded-2xl p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl ${styles}`}
    >
      <div className="pointer-events-none absolute -right-12 -bottom-12 h-36 w-36 rounded-full border border-current opacity-15 transition-transform duration-700 group-hover:scale-125" />
      <div className="pointer-events-none absolute -right-4 -top-4 h-24 w-24 rounded-full bg-current opacity-5 blur-2xl" />

      <div className="flex items-center justify-between">
        <span className="text-[10px] font-extrabold uppercase tracking-[.18em] opacity-80">
          {label}
        </span>
        <span className={`rounded-full px-2.5 py-0.5 text-[9px] font-bold tracking-wider backdrop-blur-xs ${pillStyles}`}>
          LIVE
        </span>
      </div>

      <div className="mt-4 font-display text-[32px] font-medium leading-none tracking-tight">
        {value}
      </div>
      <div className="mt-3 text-[11.5px] font-medium opacity-75">{sub}</div>
    </div>
  );
}

function MetricCard({
  label,
  value,
  sub,
  tone,
  icon,
}: {
  label: string;
  value: any;
  sub: string;
  tone: "blue" | "sand" | "rose" | "mint";
  icon: string;
}) {
  const badgeStyle = {
    blue: "bg-gradient-to-br from-[#e8edf6] to-[#d3dfef] text-[#1d3156] border border-[#bfd2eb]",
    sand: "bg-gradient-to-br from-[#f8f1e4] to-[#ecdcbe] text-[#856336] border border-[#e1cea6]",
    rose: "bg-gradient-to-br from-[#fbebe7] to-[#f4d1c8] text-[#933d2d] border border-[#e8bcb0]",
    mint: "bg-gradient-to-br from-[#e8f4ea] to-[#cee8d2] text-[#2c5b3c] border border-[#b8dfbe]",
  }[tone];

  return (
    <div className="group relative overflow-hidden rounded-2xl border border-border/70 bg-gradient-to-b from-card to-card/85 p-5 shadow-xs transition-all duration-300 hover:-translate-y-1 hover:shadow-md hover:border-[#d6bd92]/50">
      <div className="flex items-center justify-between">
        <span className="text-[9.5px] font-bold uppercase tracking-[.14em] text-muted-foreground/85">
          {label}
        </span>
        <span
          className={`flex h-8.5 w-8.5 items-center justify-center rounded-xl shadow-xs transition-transform duration-300 group-hover:scale-110 ${badgeStyle}`}
        >
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d={icon} />
          </svg>
        </span>
      </div>
      <div className="mt-2.5 font-display text-[26px] font-semibold tracking-tight text-foreground">
        {value}
      </div>
      <div className="mt-1 text-[10.5px] font-medium text-muted-foreground/80">{sub}</div>
    </div>
  );
}

export function getCategoryIcon(name: string = ""): string {
  const n = (name || "").toLowerCase();
  if (n.includes("kostyum") || n.includes("ko'ylak") || n.includes("rubashka") || n.includes("shirt") || n.includes("suit")) return "👔";
  if (n.includes("poyabzal") || n.includes("tufli") || n.includes("krossovk") || n.includes("shoes") || n.includes("boot") || n.includes("oyoq")) return "👞";
  if (n.includes("shim") || n.includes("jeans") || n.includes("pants") || n.includes("trousers") || n.includes("bryuk")) return "👖";
  if (n.includes("kurtka") || n.includes("palto") || n.includes("jaket") || n.includes("outerwear") || n.includes("coat")) return "🧥";
  if (n.includes("sumka") || n.includes("aksessuar") || n.includes("kamar") || n.includes("bag") || n.includes("accessories")) return "🎒";
  if (n.includes("soat") || n.includes("watch")) return "⌚";
  if (n.includes("sport") || n.includes("fitnes")) return "🏃";
  return "🏷️";
}

// ---------------- 2. PRODUCTS & QUICK ADD ----------------
export function ProductsPage() {
  const { t } = useLang();
  const { toast } = useToast();
  const [items, setItems] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [catId, setCatId] = useState("");
  const [status, setStatus] = useState("all");
  const [selected, setSelected] = useState<number[]>([]);
  const [confirmBulkDelete, setConfirmBulkDelete] = useState(false);
  const [delProductId, setDelProductId] = useState<number | null>(null);
  const [draftEdits, setDraftEdits] = useState<
    Record<number, { name_uz: string; price_yuan: string }>
  >({});
  const quickInputRef = useRef<HTMLInputElement>(null);

  const load = () => {
    setLoading(true);
    const params = new URLSearchParams({ status });
    if (q.trim()) params.set("q", q.trim());
    if (catId) params.set("category_id", catId);
    Promise.all([
      adminFetch(`/api/admin/products?${params.toString()}`),
      adminFetch("/api/admin/categories"),
    ])
      .then(([prods, cats]) => {
        setItems(prods);
        setCategories(cats);
      })
      .catch((e) => toast(e.message, "error"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, [q, catId, status]);

  const onQuickFiles = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    const fd = new FormData();
    Array.from(files).forEach((f) => fd.append("files", f));
    try {
      const created = await adminFetch("/api/admin/products/quick", {
        method: "POST",
        body: fd,
      });
      toast(`${created.length} ta qoralama qo'shildi`);
      setStatus("draft");
      load();
    } catch (err: any) {
      toast(err.message, "error");
    } finally {
      e.target.value = "";
    }
  };

  const publishDraft = async (id: number) => {
    const d = draftEdits[id];
    if (!d?.name_uz || !d?.price_yuan) {
      toast("Nom va yuan narxini kiriting", "error");
      return;
    }
    try {
      await adminFetch(`/api/admin/products/${id}/publish`, {
        method: "POST",
        body: JSON.stringify({
          name_uz: d.name_uz,
          price_yuan: Number(d.price_yuan),
        }),
      });
      toast(t.savedToast);
      load();
    } catch (e: any) {
      toast(e.message, "error");
    }
  };

  const runBulk = async (action: string) => {
    if (selected.length === 0) return;
    try {
      await adminFetch("/api/admin/products/bulk", {
        method: "POST",
        body: JSON.stringify({ ids: selected, action }),
      });
      setSelected([]);
      toast(t.savedToast);
      load();
    } catch (e: any) {
      toast(e.message, "error");
    }
  };

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Katalog · Products"
        title="Mahsulotlar katalogi"
        detail={`Jami ${items.length} ta mahsulot — narxlar sozlamalar bo‘yicha avtomatik hisoblanadi.`}
        action={
          <div className="flex flex-wrap gap-2">
            <input
              ref={quickInputRef}
              type="file"
              multiple
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
              onChange={onQuickFiles}
            />
            <Link
              to="/admin/categories"
              className="wm-btn-outline text-xs no-underline"
            >
              {t.categories}
            </Link>
            <button
              type="button"
              onClick={() => quickInputRef.current?.click()}
              className="wm-btn-sand text-xs"
            >
              + {t.quickAdd}
            </button>
            <Link
              to="/admin/products/new"
              className="wm-btn text-xs no-underline"
            >
              + {t.newProduct}
            </Link>
          </div>
        }
      />

      {/* Category Pill Bar (Interactive Luxury Badges) */}
      <div className="flex flex-wrap items-center gap-2">
        {[
          { id: "", name_uz: "Barchasi" },
          ...categories.map((c) => ({ id: String(c.id), name_uz: c.name_uz })),
        ].map((c) => {
          const active = catId === c.id;
          const icon = c.id ? getCategoryIcon(c.name_uz) : "✨";
          return (
            <button
              key={c.id || "all"}
              type="button"
              onClick={() => setCatId(c.id)}
              className={`inline-flex items-center gap-1.5 rounded-2xl px-3.5 py-1.5 text-[11px] font-bold transition-all duration-200 cursor-pointer ${
                active
                  ? "bg-[#172641] text-[#f5f1e8] shadow-sm ring-2 ring-[#d6bd92]/50 scale-[1.02]"
                  : "border border-border/80 bg-card text-muted-foreground hover:border-[#172641]/35 hover:text-foreground"
              }`}
            >
              <span>{icon}</span>
              <span>{c.name_uz}</span>
            </button>
          );
        })}
      </div>

      {/* Filters Card */}
      <div className="rounded-2xl border border-border bg-card p-4 grid grid-cols-1 md:grid-cols-3 gap-3">
        <div>
          <label htmlFor="prod-q" className="wm-label">
            {t.search}
          </label>
          <input
            id="prod-q"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder={t.searchPlaceholder}
            className="wm-input"
          />
        </div>
        <div>
          <label htmlFor="prod-cat" className="wm-label">
            {t.categories}
          </label>
          <select
            id="prod-cat"
            value={catId}
            onChange={(e) => setCatId(e.target.value)}
            className="wm-input"
          >
            <option value="">{t.allCategories}</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name_uz}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="prod-st" className="wm-label">
            Holati
          </label>
          <select
            id="prod-st"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="wm-input"
          >
            <option value="all">Barchasi</option>
            <option value="active">Faol</option>
            <option value="hidden">Yashirin</option>
            <option value="draft">Qoralama (Quick Add)</option>
            <option value="deleted">O'chirilgan</option>
          </select>
        </div>
      </div>

      {selected.length > 0 && (
        <div className="rounded-2xl border border-border bg-card p-3.5 flex flex-wrap items-center gap-2">
          <span className="text-xs font-bold">
            Tanlangan: {selected.length}
          </span>
          <button
            type="button"
            onClick={() => runBulk("hide")}
            className="wm-btn-outline text-xs"
          >
            {t.hide}
          </button>
          <button
            type="button"
            onClick={() => runBulk("show")}
            className="wm-btn-outline text-xs"
          >
            {t.show}
          </button>
          <button
            type="button"
            onClick={() => setConfirmBulkDelete(true)}
            className="wm-btn-outline text-xs text-[#a3463c]"
          >
            {t.delete}
          </button>
        </div>
      )}

      {loading ? (
        <SkeletonList count={4} />
      ) : items.length === 0 ? (
        <EmptyState text="Mahsulotlar topilmadi" />
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {items.map((p) => {
            const checked = selected.includes(p.id);
            const firstImg = p.images?.[0];
            return (
              <article
                key={p.id}
                className="group overflow-hidden rounded-2xl border border-border bg-card transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg flex flex-col justify-between"
              >
                <div>
                  {/* Image Header */}
                  <div className="relative h-[185px] overflow-hidden bg-[#ece5d8]">
                    {firstImg ? (
                      <img
                        src={`/uploads/${firstImg.thumb}`}
                        alt={p.name_uz}
                        className="h-full w-full object-cover transition duration-500 group-hover:scale-[1.03]"
                      />
                    ) : (
                      <div className="flex h-full items-center justify-center font-display text-2xl text-[#8d7f68]">
                        {p.name_uz?.slice(0, 1) || "W"}
                      </div>
                    )}

                    {/* Top-left Checkbox + SaleType Badge */}
                    <div className="absolute left-3 top-3 flex items-center gap-2">
                      <input
                        type="checkbox"
                        aria-label={`Tanlash ${p.name_uz}`}
                        checked={checked}
                        onChange={(e) =>
                          setSelected((prev) =>
                            e.target.checked
                              ? [...prev, p.id]
                              : prev.filter((x) => x !== p.id)
                          )
                        }
                        className="h-4 w-4 rounded accent-[#172641]"
                      />
                      <span
                        className={`rounded-full px-2.5 py-1 text-[9px] font-bold uppercase tracking-wider backdrop-blur-md ${
                          p.sale_type === "stock"
                            ? "bg-[#22352c]/90 text-[#d8f0df]"
                            : "bg-[#172641]/90 text-[#f3e7d1]"
                        }`}
                      >
                        {p.sale_type === "stock"
                          ? t.inStockBadge
                          : t.preorderBadge}
                      </span>
                    </div>

                    {/* Top-right Active Badge */}
                    <span
                      className={`absolute right-3 top-3 rounded-full px-2.5 py-1 text-[9px] font-bold ${
                        p.is_draft
                          ? "bg-[#f1e7d3] text-[#8d6e43]"
                          : p.active
                          ? "bg-[#e6f2e8] text-[#397252]"
                          : "bg-black/65 text-white"
                      }`}
                    >
                      {p.is_draft
                        ? "Qoralama"
                        : p.active
                        ? "Faol"
                        : "Yashirin"}
                    </span>
                  </div>

                  {/* Card Body */}
                  <div className="p-4">
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <h3 className="truncate text-[14px] font-extrabold">
                          {p.name_uz}
                        </h3>
                        <p className="truncate text-[11px] text-muted-foreground">
                          {p.name_ru || "—"}
                        </p>
                      </div>
                      {p.featured && (
                        <span className="shrink-0 text-[10px] font-bold text-[#aa8a5e]">
                          ★ Featured
                        </span>
                      )}
                    </div>

                    <div className="mt-3 flex items-baseline justify-between border-t border-border/70 pt-3">
                      <div>
                        <div className="font-display text-[20px] font-medium tracking-[-.02em]">
                          {formatPrice(p.selling_price)}
                        </div>
                        <div className="text-[10px] text-muted-foreground">
                          ¥{p.price_yuan} · {p.weight_kg} kg
                        </div>
                      </div>
                      <div className="flex flex-wrap justify-end gap-1">
                        {(p.variants || []).slice(0, 3).map((v: any, idx: number) => (
                          <span
                            key={idx}
                            className="rounded-md bg-muted px-2 py-0.5 text-[10px] font-semibold"
                          >
                            {v.size} · {v.color}
                            {p.sale_type === "stock" ? ` (${v.stock})` : ""}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Quick-Add Draft Inline Publish */}
                    {p.is_draft && (
                      <div className="mt-3 space-y-2 rounded-xl border border-[#e4d5b7] bg-[#faf5ea] p-3">
                        <div className="text-[10px] font-bold uppercase tracking-wider text-[#8d6e43]">
                          Tezkor e'lon qilish
                        </div>
                        <input
                          placeholder="Mahsulot nomi (UZ)"
                          aria-label="Qoralama nomi"
                          value={draftEdits[p.id]?.name_uz ?? ""}
                          onChange={(e) =>
                            setDraftEdits((prev) => ({
                              ...prev,
                              [p.id]: {
                                name_uz: e.target.value,
                                price_yuan:
                                  prev[p.id]?.price_yuan ??
                                  String(p.price_yuan || ""),
                              },
                            }))
                          }
                          className="wm-input text-xs"
                        />
                        <input
                          type="number"
                          placeholder="Narxi (Yuan)"
                          aria-label="Qoralama yuan narxi"
                          value={draftEdits[p.id]?.price_yuan ?? ""}
                          onChange={(e) =>
                            setDraftEdits((prev) => ({
                              ...prev,
                              [p.id]: {
                                name_uz: prev[p.id]?.name_uz ?? p.name_uz,
                                price_yuan: e.target.value,
                              },
                            }))
                          }
                          className="wm-input text-xs"
                        />
                        <button
                          type="button"
                          onClick={() => publishDraft(p.id)}
                          className="wm-btn text-xs w-full"
                        >
                          Saqlash va faollashtirish
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Card Actions Footer */}
                <div className="flex flex-wrap items-center justify-between gap-1.5 border-t border-border/60 bg-[#faf8f3] px-4 py-2.5 text-[11px] font-bold">
                  <div className="flex flex-wrap items-center gap-2">
                    <Link
                      to={`/admin/products/${p.id}`}
                      className="text-primary no-underline hover:underline"
                    >
                      {t.edit}
                    </Link>
                    <button
                      type="button"
                      onClick={async () => {
                        await adminFetch(
                          `/api/admin/products/${p.id}/duplicate`,
                          { method: "POST" }
                        );
                        toast(t.savedToast);
                        load();
                      }}
                      className="text-muted-foreground hover:text-foreground bg-transparent border-0 cursor-pointer p-0 font-bold text-[11px]"
                    >
                      {t.duplicate}
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        const url = `https://t.me/Withmoreuz_bot?start=prod_${p.id}_instagram`;
                        navigator.clipboard?.writeText(url);
                        toast("📸 Mahsulotning Instagram havolasi nusxalandi!");
                      }}
                      title="Instagram Stories, Reels yoki Direct uchun maxsus mahsulot havolasi"
                      className="text-[#8d6e43] hover:text-[#172641] bg-transparent border-0 cursor-pointer p-0 font-bold text-[11px]"
                    >
                      📸 Insta link
                    </button>
                    <button
                      type="button"
                      onClick={async () => {
                        await adminFetch(`/api/admin/products/${p.id}`, {
                          method: "PATCH",
                          body: JSON.stringify({ active: !p.active }),
                        });
                        load();
                      }}
                      className="text-muted-foreground hover:text-foreground bg-transparent border-0 cursor-pointer p-0 font-bold text-[11px]"
                    >
                      {p.active ? t.hide : t.show}
                    </button>
                  </div>

                  {p.deleted ? (
                    <button
                      type="button"
                      onClick={async () => {
                        await adminFetch(
                          `/api/admin/products/${p.id}/restore`,
                          { method: "POST" }
                        );
                        load();
                      }}
                      className="text-[#397252] bg-transparent border-0 cursor-pointer p-0 font-bold text-[11px]"
                    >
                      {t.restore}
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={() => setDelProductId(p.id)}
                      className="text-[#a3463c] bg-transparent border-0 cursor-pointer p-0 font-bold text-[11px]"
                    >
                      {t.delete}
                    </button>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      )}

      <ConfirmModal
        open={confirmBulkDelete}
        title={t.confirmDelete}
        onCancel={() => setConfirmBulkDelete(false)}
        onConfirm={() => {
          setConfirmBulkDelete(false);
          runBulk("delete");
        }}
      />

      <ConfirmModal
        open={delProductId !== null}
        title={t.confirmDelete}
        onCancel={() => setDelProductId(null)}
        onConfirm={async () => {
          const id = delProductId;
          setDelProductId(null);
          if (!id) return;
          await adminFetch(`/api/admin/products/${id}`, { method: "DELETE" });
          toast(t.deletedToast);
          load();
        }}
      />
    </div>
  );
}

// ---------------- FULL PRODUCT FORM ----------------
export function ProductFormPage() {
  const { id } = useParams();
  const isNew = !id;
  const navigate = useNavigate();
  const { t } = useLang();
  const { toast } = useToast();

  const [categories, setCategories] = useState<any[]>([]);
  const [settings, setSettings] = useState<any>({
    yuan_rate: "1750",
    margin_pct: "25",
    shipping_per_kg: "65000",
  });
  const [form, setForm] = useState<any>({
    name_uz: "",
    name_ru: "",
    desc_uz: "",
    desc_ru: "",
    category_id: "",
    material: "",
    price_yuan: 200,
    weight_kg: 0.5,
    manual_price: "",
    sale_type: "preorder",
    featured: false,
    active: true,
    size_chart: [{ size: "M", chest: "104", waist: "92", length: "72" }],
    variants: [{ size: "M", color: "Ko'k", stock: 5 }],
    images: [],
  });
  const [supplierUrl, setSupplierUrl] = useState("");
  const [dragIdx, setDragIdx] = useState<number | null>(null);

  useEffect(() => {
    adminFetch("/api/admin/categories").then(setCategories);
    adminFetch("/api/admin/settings")
      .then(setSettings)
      .catch(() => {});
    if (!isNew) {
      adminFetch(`/api/admin/products?status=all`).then((list) => {
        const found = list.find((x: any) => String(x.id) === String(id));
        if (found) {
          setForm({
            ...found,
            category_id: found.category_id || "",
            manual_price: found.manual_price || "",
          });
        }
      });
      adminFetch(`/api/admin/ops/supplier/${id}`)
        .then((res) => {
          if (res?.url) setSupplierUrl(res.url);
        })
        .catch(() => {});
    }
  }, [id, isNew]);

  const livePrice = calcSellingPrice(
    Number(form.price_yuan) || 0,
    Number(form.weight_kg) || 0,
    Number(settings.yuan_rate) || 1750,
    Number(settings.shipping_per_kg) || 65000,
    Number(settings.margin_pct) || 25,
    form.manual_price ? Number(form.manual_price) : null
  );

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      ...form,
      category_id: form.category_id ? Number(form.category_id) : null,
      price_yuan: Number(form.price_yuan),
      weight_kg: Number(form.weight_kg),
      manual_price: form.manual_price ? Number(form.manual_price) : null,
      is_draft: false,
    };
    try {
      if (isNew) {
        const created = await adminFetch("/api/admin/products", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        toast(t.savedToast);
        if (supplierUrl.trim()) {
          adminFetch(`/api/admin/ops/supplier/${created.id}`, {
            method: "PUT",
            body: JSON.stringify({ url: supplierUrl.trim() }),
          }).catch(() => {});
        }
        navigate(`/admin/products/${created.id}`);
      } else {
        const updated = await adminFetch(`/api/admin/products/${id}`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        });
        if (supplierUrl.trim() !== undefined) {
          adminFetch(`/api/admin/ops/supplier/${id}`, {
            method: "PUT",
            body: JSON.stringify({ url: supplierUrl.trim() }),
          }).catch(() => {});
        }
        setForm({
          ...updated,
          category_id: updated.category_id || "",
          manual_price: updated.manual_price || "",
        });
        toast(t.savedToast);
      }
    } catch (err: any) {
      toast(err.message, "error");
    }
  };

  const uploadPhotos = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || !id) return;
    for (const f of Array.from(files)) {
      const fd = new FormData();
      fd.append("files", f);
      fd.append("file", f);
      try {
        const updated = await adminFetch(`/api/admin/products/${id}/images`, {
          method: "POST",
          body: fd,
        });
        setForm((prev: any) => ({ ...prev, images: updated.images }));
      } catch (err: any) {
        toast(err.message, "error");
      }
    }
    e.target.value = "";
  };

  const reorderImages = async (imgs: any[]) => {
    setForm((prev: any) => ({ ...prev, images: imgs }));
    if (!id) return;
    await adminFetch(`/api/admin/products/${id}/images/order`, {
      method: "PUT",
      body: JSON.stringify({ image_ids: imgs.map((x) => x.id) }),
    });
  };

  return (
    <form onSubmit={save} className="space-y-5 max-w-4xl">
      <PageHeader
        eyebrow="Katalog · Product Editor"
        title={isNew ? t.newProduct : "Mahsulotni tahrirlash"}
        action={
          <Link
            to="/admin/products"
            className="wm-btn-outline text-xs no-underline"
          >
            ← Orqaga
          </Link>
        }
      />

      <div className="rounded-2xl border border-border bg-card p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="pf-name-uz" className="wm-label">
            Nomi (UZ) *
          </label>
          <input
            id="pf-name-uz"
            required
            value={form.name_uz}
            onChange={(e) => setForm({ ...form, name_uz: e.target.value })}
            className="wm-input"
          />
        </div>
        <div>
          <label htmlFor="pf-name-ru" className="wm-label">
            Nomi (RU)
          </label>
          <input
            id="pf-name-ru"
            value={form.name_ru}
            onChange={(e) => setForm({ ...form, name_ru: e.target.value })}
            className="wm-input"
          />
        </div>
        <div>
          <label htmlFor="pf-desc-uz" className="wm-label">
            Tavsif (UZ)
          </label>
          <textarea
            id="pf-desc-uz"
            rows={3}
            value={form.desc_uz}
            onChange={(e) => setForm({ ...form, desc_uz: e.target.value })}
            className="wm-input"
          />
        </div>
        <div>
          <label htmlFor="pf-desc-ru" className="wm-label">
            Tavsif (RU)
          </label>
          <textarea
            id="pf-desc-ru"
            rows={3}
            value={form.desc_ru}
            onChange={(e) => setForm({ ...form, desc_ru: e.target.value })}
            className="wm-input"
          />
        </div>
        <div>
          <label htmlFor="pf-cat" className="wm-label">
            Kategoriya
          </label>
          <select
            id="pf-cat"
            value={form.category_id}
            onChange={(e) => setForm({ ...form, category_id: e.target.value })}
            className="wm-input"
          >
            <option value="">Tanlanmagan</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name_uz}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="pf-mat" className="wm-label">
            {t.material}
          </label>
          <input
            id="pf-mat"
            value={form.material}
            onChange={(e) => setForm({ ...form, material: e.target.value })}
            className="wm-input"
          />
        </div>
        <div>
          <label htmlFor="pf-yuan" className="wm-label">
            {t.priceYuan}
          </label>
          <input
            id="pf-yuan"
            type="number"
            step="0.01"
            value={form.price_yuan}
            onChange={(e) => setForm({ ...form, price_yuan: e.target.value })}
            className="wm-input"
          />
        </div>
        <div>
          <label htmlFor="pf-kg" className="wm-label">
            {t.weightKg}
          </label>
          <input
            id="pf-kg"
            type="number"
            step="0.1"
            value={form.weight_kg}
            onChange={(e) => setForm({ ...form, weight_kg: e.target.value })}
            className="wm-input"
          />
        </div>
        <div>
          <label htmlFor="pf-manual" className="wm-label">
            {t.manualPriceUzs}
          </label>
          <input
            id="pf-manual"
            type="number"
            value={form.manual_price}
            onChange={(e) => setForm({ ...form, manual_price: e.target.value })}
            className="wm-input"
          />
        </div>
        <div className="flex flex-col justify-center rounded-xl bg-[#172641] p-4 text-[#f5f1e8]">
          <div className="text-[10px] font-bold uppercase tracking-wider text-[#d6bd92]">
            {t.calculatedPrice}
          </div>
          <div className="mt-1 font-display text-2xl font-medium">
            {formatPrice(livePrice)}
          </div>
        </div>
        <div>
          <label htmlFor="pf-sale" className="wm-label">
            Sotuv turi
          </label>
          <select
            id="pf-sale"
            value={form.sale_type}
            onChange={(e) => setForm({ ...form, sale_type: e.target.value })}
            className="wm-input"
          >
            <option value="preorder">{t.preorderBadge}</option>
            <option value="stock">{t.inStockBadge}</option>
          </select>
        </div>
        <div className="md:col-span-2">
          <label htmlFor="pf-sup" className="wm-label flex items-center justify-between">
            <span>🇨🇳 Xitoy yetkazib beruvchi havolasi (1688 / Taobao / Poizon link)</span>
            <span className="text-[10px] text-muted-foreground font-normal">Faqat admin uchun</span>
          </label>
          <div className="flex gap-2">
            <input
              id="pf-sup"
              value={supplierUrl}
              onChange={(e) => setSupplierUrl(e.target.value)}
              placeholder="https://detail.1688.com/offer/... yoki taobao link"
              className="wm-input flex-1"
            />
            {supplierUrl.startsWith("http") && (
              <a
                href={supplierUrl}
                target="_blank"
                rel="noreferrer"
                className="wm-btn-outline text-xs px-3.5 py-2 inline-flex items-center no-underline shrink-0"
              >
                ↗ Ochish
              </a>
            )}
          </div>
        </div>
        <div className="flex items-center gap-5 pt-5">
          <label className="flex items-center gap-2 text-xs font-bold">
            <input
              type="checkbox"
              checked={form.featured}
              onChange={(e) => setForm({ ...form, featured: e.target.checked })}
              className="accent-[#172641]"
            />
            Tanlangan (Featured)
          </label>
          <label className="flex items-center gap-2 text-xs font-bold">
            <input
              type="checkbox"
              checked={form.active}
              onChange={(e) => setForm({ ...form, active: e.target.checked })}
              className="accent-[#172641]"
            />
            Faol (Active)
          </label>
        </div>
      </div>

      {/* Photos (up to 6, drag to reorder, first is main) */}
      {!isNew && (
        <div className="rounded-2xl border border-border bg-card p-6 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <label htmlFor="pf-photos" className="wm-label mb-0">
              Rasmlar (ko'pi bilan 6 ta, birinchisi asosiy — surib tartiblang)
            </label>
            <input
              id="pf-photos"
              type="file"
              multiple
              accept="image/jpeg,image/png,image/webp"
              onChange={uploadPhotos}
              className="text-xs"
            />
          </div>
          <div className="flex flex-wrap gap-3">
            {(form.images || []).map((img: any, idx: number) => (
              <div
                key={img.id}
                draggable
                onDragStart={() => setDragIdx(idx)}
                onDragOver={(e) => e.preventDefault()}
                onDrop={() => {
                  if (dragIdx === null || dragIdx === idx) return;
                  const copy = [...form.images];
                  const [moved] = copy.splice(dragIdx, 1);
                  copy.splice(idx, 0, moved);
                  setDragIdx(null);
                  reorderImages(copy);
                }}
                className="p-2 border border-border rounded-xl space-y-1.5 bg-[#faf8f3]"
              >
                <img
                  src={`/uploads/${img.thumb}`}
                  alt=""
                  className="w-24 h-28 object-cover rounded-lg"
                />
                <div className="flex justify-between gap-1 px-1">
                  <span className="text-[10px] font-bold">
                    {idx === 0 ? "Asosiy" : `#${idx + 1}`}
                  </span>
                  <button
                    type="button"
                    onClick={async () => {
                      const updated = await adminFetch(
                        `/api/admin/products/${id}/images/${img.id}`,
                        { method: "DELETE" }
                      );
                      setForm((prev: any) => ({
                        ...prev,
                        images: updated.images,
                      }));
                    }}
                    className="text-[10px] font-bold text-[#a3463c] underline cursor-pointer bg-transparent border-0 p-0"
                  >
                    {t.delete}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Variants */}
      <div className="rounded-2xl border border-border bg-card p-6 space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-sm font-extrabold">
            Variantlar (o'lcham + rang + qoldiq)
          </div>
          <button
            type="button"
            onClick={() =>
              setForm({
                ...form,
                variants: [
                  ...(form.variants || []),
                  { size: "", color: "", stock: 0 },
                ],
              })
            }
            className="wm-btn-outline text-xs"
          >
            + Variant
          </button>
        </div>
        {(form.variants || []).map((v: any, idx: number) => (
          <div key={idx} className="grid grid-cols-4 gap-2 items-end">
            <div>
              <label htmlFor={`vsz-${idx}`} className="wm-label">
                {t.size}
              </label>
              <input
                id={`vsz-${idx}`}
                value={v.size}
                onChange={(e) => {
                  const next = [...form.variants];
                  next[idx] = { ...v, size: e.target.value };
                  setForm({ ...form, variants: next });
                }}
                className="wm-input"
              />
            </div>
            <div>
              <label htmlFor={`vcol-${idx}`} className="wm-label">
                {t.color}
              </label>
              <input
                id={`vcol-${idx}`}
                value={v.color}
                onChange={(e) => {
                  const next = [...form.variants];
                  next[idx] = { ...v, color: e.target.value };
                  setForm({ ...form, variants: next });
                }}
                className="wm-input"
              />
            </div>
            <div>
              <label htmlFor={`vstk-${idx}`} className="wm-label">
                Qoldiq
              </label>
              <input
                id={`vstk-${idx}`}
                type="number"
                value={v.stock}
                onChange={(e) => {
                  const next = [...form.variants];
                  next[idx] = { ...v, stock: Number(e.target.value) };
                  setForm({ ...form, variants: next });
                }}
                className="wm-input"
              />
            </div>
            <button
              type="button"
              onClick={() =>
                setForm({
                  ...form,
                  variants: form.variants.filter(
                    (_: any, i: number) => i !== idx
                  ),
                })
              }
              className="wm-btn-outline text-xs"
            >
              {t.remove}
            </button>
          </div>
        ))}
      </div>

      {/* Size Chart (cm) */}
      <div className="rounded-2xl border border-border bg-card p-6 space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-sm font-extrabold">{t.sizeChart}</div>
          <button
            type="button"
            onClick={() =>
              setForm({
                ...form,
                size_chart: [
                  ...(form.size_chart || []),
                  { size: "", chest: "", waist: "", length: "" },
                ],
              })
            }
            className="wm-btn-outline text-xs"
          >
            + Qator
          </button>
        </div>
        {(form.size_chart || []).map((row: any, idx: number) => (
          <div key={idx} className="grid grid-cols-5 gap-2 items-end">
            <div>
              <label htmlFor={`sc-s-${idx}`} className="wm-label">
                {t.size}
              </label>
              <input
                id={`sc-s-${idx}`}
                value={row.size || ""}
                onChange={(e) => {
                  const next = [...form.size_chart];
                  next[idx] = { ...row, size: e.target.value };
                  setForm({ ...form, size_chart: next });
                }}
                className="wm-input"
              />
            </div>
            <div>
              <label htmlFor={`sc-c-${idx}`} className="wm-label">
                {t.chest}
              </label>
              <input
                id={`sc-c-${idx}`}
                value={row.chest || ""}
                onChange={(e) => {
                  const next = [...form.size_chart];
                  next[idx] = { ...row, chest: e.target.value };
                  setForm({ ...form, size_chart: next });
                }}
                className="wm-input"
              />
            </div>
            <div>
              <label htmlFor={`sc-w-${idx}`} className="wm-label">
                {t.waist}
              </label>
              <input
                id={`sc-w-${idx}`}
                value={row.waist || ""}
                onChange={(e) => {
                  const next = [...form.size_chart];
                  next[idx] = { ...row, waist: e.target.value };
                  setForm({ ...form, size_chart: next });
                }}
                className="wm-input"
              />
            </div>
            <div>
              <label htmlFor={`sc-l-${idx}`} className="wm-label">
                {t.length}
              </label>
              <input
                id={`sc-l-${idx}`}
                value={row.length || ""}
                onChange={(e) => {
                  const next = [...form.size_chart];
                  next[idx] = { ...row, length: e.target.value };
                  setForm({ ...form, size_chart: next });
                }}
                className="wm-input"
              />
            </div>
            <button
              type="button"
              onClick={() =>
                setForm({
                  ...form,
                  size_chart: form.size_chart.filter(
                    (_: any, i: number) => i !== idx
                  ),
                })
              }
              className="wm-btn-outline text-xs"
            >
              {t.remove}
            </button>
          </div>
        ))}
      </div>

      <button type="submit" className="wm-btn">
        {t.save}
      </button>
    </form>
  );
}

// ---------------- 3. CATEGORIES ----------------
export function CategoriesPage() {
  const { t } = useLang();
  const { toast } = useToast();
  const [cats, setCats] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [nameUz, setNameUz] = useState("");
  const [nameRu, setNameRu] = useState("");
  const [delId, setDelId] = useState<number | null>(null);
  const [editItem, setEditItem] = useState<{
    id: number;
    name_uz: string;
    name_ru: string;
  } | null>(null);

  const load = () => {
    setLoading(true);
    adminFetch("/api/admin/categories")
      .then(setCats)
      .catch((e) => toast(e.message, "error"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const add = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nameUz.trim()) return;
    try {
      await adminFetch("/api/admin/categories", {
        method: "POST",
        body: JSON.stringify({ name_uz: nameUz.trim(), name_ru: nameRu.trim() }),
      });
      setNameUz("");
      setNameRu("");
      toast(t.savedToast);
      load();
    } catch (err: any) {
      toast(err.message, "error");
    }
  };

  const handleEditSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editItem || !editItem.name_uz.trim()) return;
    try {
      await adminFetch(`/api/admin/categories/${editItem.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          name_uz: editItem.name_uz.trim(),
          name_ru: editItem.name_ru.trim(),
        }),
      });
      toast(t.savedToast);
      setEditItem(null);
      load();
    } catch (err: any) {
      toast(err.message, "error");
    }
  };

  const move = async (idx: number, dir: number) => {
    const next = [...cats];
    const target = idx + dir;
    if (target < 0 || target >= next.length) return;
    [next[idx], next[target]] = [next[target], next[idx]];
    setCats(next);
    await adminFetch("/api/admin/categories/order", {
      method: "PUT",
      body: JSON.stringify({ ids: next.map((c) => c.id) }),
    });
  };

  const filtered = cats.filter(
    (c) =>
      c.name_uz.toLowerCase().includes(q.toLowerCase()) ||
      (c.name_ru && c.name_ru.toLowerCase().includes(q.toLowerCase()))
  );

  const totalProducts = cats.reduce(
    (sum, c) => sum + (Number(c.products) || 0),
    0
  );

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Katalog Strukturalari · Categories"
        title="Kategoriyalar va Bo‘limlar"
        detail="Mini App va Admin paneldagi mahsulotlar toifalarini tartibga solish, nomlash va ierarxiyasini boshqarish."
        action={
          <Link
            to="/admin/products"
            className="wm-btn-outline text-xs no-underline"
          >
            ← Mahsulotlarga qaytish
          </Link>
        }
      />

      {/* Categories KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="relative overflow-hidden rounded-2xl border border-border/80 bg-gradient-to-b from-card to-card/85 p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-[.14em] text-muted-foreground">
              Jami Bo'limlar
            </span>
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#e8edf6] text-lg">
              🏷️
            </span>
          </div>
          <div className="mt-2.5 font-display text-[26px] font-bold text-foreground">
            {cats.length} ta
          </div>
          <div className="mt-1 text-[10.5px] text-muted-foreground">
            Do'konda faol katalog bo'limlari
          </div>
        </div>

        <div className="relative overflow-hidden rounded-2xl border border-border/80 bg-gradient-to-b from-card to-card/85 p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-[.14em] text-muted-foreground">
              Biriktirilgan Mahsulotlar
            </span>
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#f8f1e4] text-lg">
              👔
            </span>
          </div>
          <div className="mt-2.5 font-display text-[26px] font-bold text-foreground">
            {totalProducts} dona
          </div>
          <div className="mt-1 text-[10.5px] text-muted-foreground">
            Bo'limlar bo'yicha toifalangan tovarlar
          </div>
        </div>

        <div className="relative overflow-hidden rounded-2xl border border-border/80 bg-gradient-to-b from-card to-card/85 p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-[.14em] text-muted-foreground">
              Sinxronizatsiya
            </span>
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#e8f4ea] text-lg">
              ⚡
            </span>
          </div>
          <div className="mt-2.5 font-display text-[26px] font-bold text-[#356348]">
            Avtomatik
          </div>
          <div className="mt-1 text-[10.5px] text-muted-foreground">
            Mini App chip karuselida real vaqtda yangilanadi
          </div>
        </div>
      </div>

      {/* Add New Category Studio Card */}
      <div className="rounded-2xl border border-[#d6bd92]/40 bg-gradient-to-br from-card via-card to-[#faf6ee] p-5 shadow-xs space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border/70 pb-3">
          <div>
            <h3 className="text-sm font-bold text-foreground">
              Yangi bo'lim yaratish
            </h3>
            <p className="text-[11px] text-muted-foreground">
              Kategoriya kiritilganda uning ikonkasi avtomatik tanlanadi va Mini Appda aks etadi.
            </p>
          </div>
          {nameUz.trim() && (
            <div className="inline-flex items-center gap-2 rounded-2xl border border-[#172641]/15 bg-white px-3 py-1.5 shadow-xs">
              <span className="text-base">{getCategoryIcon(nameUz)}</span>
              <span className="text-xs font-bold text-[#172641]">{nameUz}</span>
              {nameRu && (
                <span className="text-[11px] text-muted-foreground">/ {nameRu}</span>
              )}
            </div>
          )}
        </div>

        <form
          onSubmit={add}
          className="grid grid-cols-1 md:grid-cols-5 gap-3 items-end"
        >
          <div className="md:col-span-2">
            <label htmlFor="cat-uz" className="wm-label">
              Nomi (O'zbekcha) *
            </label>
            <input
              id="cat-uz"
              required
              placeholder="Masalan: Kostyumlar, Poyabzallar, Shimlar..."
              value={nameUz}
              onChange={(e) => setNameUz(e.target.value)}
              className="wm-input"
            />
          </div>
          <div className="md:col-span-2">
            <label htmlFor="cat-ru" className="wm-label">
              Nomi (Ruscha)
            </label>
            <input
              id="cat-ru"
              placeholder="Например: Костюмы, Обувь, Брюки..."
              value={nameRu}
              onChange={(e) => setNameRu(e.target.value)}
              className="wm-input"
            />
          </div>
          <div>
            <button type="submit" className="wm-btn w-full">
              + Qo‘shish
            </button>
          </div>
        </form>
      </div>

      {/* Search & Filter */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="relative w-full max-w-sm">
          <input
            id="cat-search"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Bo‘lim nomidan qidirish..."
            className="wm-input pl-9"
          />
          <svg
            width="15"
            height="15"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none"
          >
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
        </div>
        <div className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider">
          {filtered.length} ta bo'lim topildi
        </div>
      </div>

      {/* Category Cards Grid */}
      {loading ? (
        <SkeletonList count={3} />
      ) : filtered.length === 0 ? (
        <EmptyState text="Kategoriyalar topilmadi" />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((c, idx) => {
            const icon = getCategoryIcon(c.name_uz);
            return (
              <div
                key={c.id}
                className="group relative flex flex-col justify-between overflow-hidden rounded-2xl border border-border/80 bg-gradient-to-b from-card to-card/90 p-5 shadow-xs transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:border-[#d6bd92]/60"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-3">
                      <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-[#172641]/10 via-[#172641]/5 to-[#c5a776]/15 text-2xl border border-[#172641]/10 shadow-xs transition-transform duration-300 group-hover:scale-105">
                        {icon}
                      </div>
                      <div className="min-w-0">
                        <h4 className="truncate text-[15px] font-bold text-foreground">
                          {c.name_uz}
                        </h4>
                        <div className="truncate text-xs text-muted-foreground">
                          {c.name_ru || "—"}
                        </div>
                      </div>
                    </div>
                    <span className="rounded-full bg-[#172641]/5 px-2.5 py-0.5 text-[10px] font-bold text-muted-foreground">
                      #{idx + 1}
                    </span>
                  </div>

                  <div className="mt-4 flex items-center justify-between border-t border-border/60 pt-3">
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-[#faf5ea] px-3 py-1 text-[11px] font-bold text-[#8a6c43] border border-[#e8ddc7]">
                      <span>📦</span>
                      <span>{c.products || 0} ta mahsulot</span>
                    </span>
                    <Link
                      to="/admin/products"
                      className="text-[11px] font-bold text-primary no-underline hover:underline"
                    >
                      Katalogda ko‘rish →
                    </Link>
                  </div>
                </div>

                {/* Actions Toolbar */}
                <div className="mt-4 flex items-center justify-between border-t border-border/60 pt-3">
                  <div className="flex items-center gap-1">
                    <button
                      type="button"
                      title="Yuqoriga surish"
                      onClick={() => move(idx, -1)}
                      disabled={idx === 0}
                      className="flex h-8 w-8 items-center justify-center rounded-lg border border-border bg-background text-xs font-bold transition hover:bg-muted disabled:opacity-30 cursor-pointer"
                    >
                      ↑
                    </button>
                    <button
                      type="button"
                      title="Pastga surish"
                      onClick={() => move(idx, 1)}
                      disabled={idx === filtered.length - 1}
                      className="flex h-8 w-8 items-center justify-center rounded-lg border border-border bg-background text-xs font-bold transition hover:bg-muted disabled:opacity-30 cursor-pointer"
                    >
                      ↓
                    </button>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() =>
                        setEditItem({
                          id: c.id,
                          name_uz: c.name_uz,
                          name_ru: c.name_ru || "",
                        })
                      }
                      className="rounded-lg border border-border px-3 py-1 text-xs font-bold text-foreground transition hover:bg-muted cursor-pointer"
                    >
                      {t.edit}
                    </button>
                    <button
                      type="button"
                      onClick={() => setDelId(c.id)}
                      className="rounded-lg border border-border px-3 py-1 text-xs font-bold text-[#a3463c] transition hover:bg-[#faeae5] cursor-pointer"
                    >
                      {t.delete}
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Edit Category Modal */}
      {editItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4">
          <div className="w-full max-w-md rounded-2xl border border-border bg-card p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div className="flex items-center gap-2">
                <span className="text-xl">{getCategoryIcon(editItem.name_uz)}</span>
                <h3 className="text-base font-bold text-foreground">
                  Bo‘limni tahrirlash
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setEditItem(null)}
                className="text-muted-foreground hover:text-foreground text-sm cursor-pointer"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleEditSave} className="space-y-4">
              <div>
                <label className="wm-label">Nomi (O'zbekcha) *</label>
                <input
                  required
                  value={editItem.name_uz}
                  onChange={(e) =>
                    setEditItem({ ...editItem, name_uz: e.target.value })
                  }
                  className="wm-input"
                />
              </div>
              <div>
                <label className="wm-label">Nomi (Ruscha)</label>
                <input
                  value={editItem.name_ru}
                  onChange={(e) =>
                    setEditItem({ ...editItem, name_ru: e.target.value })
                  }
                  className="wm-input"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setEditItem(null)}
                  className="wm-btn-outline text-xs"
                >
                  {t.cancel}
                </button>
                <button type="submit" className="wm-btn text-xs">
                  {t.save}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        open={delId !== null}
        title={t.confirmDelete}
        onCancel={() => setDelId(null)}
        onConfirm={async () => {
          const id = delId;
          setDelId(null);
          try {
            await adminFetch(`/api/admin/categories/${id}`, {
              method: "DELETE",
            });
            toast(t.deletedToast);
            load();
          } catch (e: any) {
            toast(e.message, "error");
          }
        }}
      />
    </div>
  );
}
