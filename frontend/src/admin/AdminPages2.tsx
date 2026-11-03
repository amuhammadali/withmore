import React, { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { adminFetch } from "../api";
import { ALL_STATUSES, calcSellingPrice, formatPrice, getStatusLabel, STATUS_LABELS, useLang } from "../i18n";
import {
  ConfirmModal,
  EmptyState,
  SkeletonList,
  StatusBadge,
  useToast,
} from "../ui";
import { PageHeader } from "./AdminPages";

const ALL_PERMS = [
  "products",
  "orders",
  "customers",
  "promotions",
  "settings",
  "statistics",
];

// ---------------- 4. ORDERS & DETAIL ----------------
export function OrdersPage() {
  const { t, lang } = useLang();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [items, setItems] = useState<any[]>([]);
  const [admins, setAdmins] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("");
  const [adminId, setAdminId] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [showManual, setShowManual] = useState(false);
  const [selected, setSelected] = useState<number[]>([]);
  const [bulkStatus, setBulkStatus] = useState("in_transit");
  const [bulkTracking, setBulkTracking] = useState("");
  const [bulkLoading, setBulkLoading] = useState(false);
  const [viewMode, setViewMode] = useState<"kanban" | "table">("kanban");

  const quickChangeStatus = async (orderId: number, nextStatus: string) => {
    try {
      await adminFetch(`/api/admin/orders/${orderId}`, {
        method: "PATCH",
        body: JSON.stringify({ status: nextStatus }),
      });
      toast(`Holat o'zgartirildi: ${getStatusLabel(nextStatus, lang)}`);
      load();
    } catch (err: any) {
      toast(err.message, "error");
    }
  };

  const handleBulkStatus = async () => {
    if (selected.length === 0) return;
    setBulkLoading(true);
    try {
      const res = await adminFetch("/api/admin/ops/bulk-status", {
        method: "POST",
        body: JSON.stringify({
          order_ids: selected,
          status: bulkStatus,
          tracking: bulkTracking,
        }),
      });
      toast(`${res.updated} ta buyurtma "${res.status_uz}" ga o'tkazildi!`);
      setSelected([]);
      setBulkTracking("");
      load();
    } catch (e: any) {
      toast(e.message, "error");
    } finally {
      setBulkLoading(false);
    }
  };

  const toggleSelectAll = () => {
    if (selected.length === items.length) {
      setSelected([]);
    } else {
      setSelected(items.map((i) => i.id));
    }
  };

  const load = () => {
    setLoading(true);
    const params = new URLSearchParams();
    if (q.trim()) params.set("q", q.trim());
    if (status) params.set("status", status);
    if (adminId) params.set("admin_id", adminId);
    if (dateFrom) params.set("date_from", dateFrom);
    if (dateTo) params.set("date_to", dateTo);
    Promise.all([
      adminFetch(`/api/admin/orders?${params.toString()}`),
      adminFetch("/api/admin/orders/admins"),
    ])
      .then(([res, adms]) => {
        setItems(res.items || []);
        setAdmins(adms || []);
      })
      .catch((e) => toast(e.message, "error"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, [q, status, adminId, dateFrom, dateTo]);

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Savdo · Orders"
        title="Buyurtmalar"
        detail="Har bir buyurtma holati va mijoz ma’lumotlari."
        action={
          <div className="flex flex-wrap items-center gap-2.5">
            {/* View Mode Switcher: Kanban vs Table */}
            <div className="flex items-center rounded-xl border border-border bg-[#efe9dc]/70 p-1">
              <button
                type="button"
                onClick={() => setViewMode("kanban")}
                className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-bold transition cursor-pointer border-0 ${
                  viewMode === "kanban"
                    ? "bg-[#172641] text-[#f5f1e8] shadow-sm"
                    : "bg-transparent text-muted-foreground hover:text-foreground"
                }`}
              >
                <span>🗂️</span>
                <span>Kanban</span>
              </button>
              <button
                type="button"
                onClick={() => setViewMode("table")}
                className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-bold transition cursor-pointer border-0 ${
                  viewMode === "table"
                    ? "bg-[#172641] text-[#f5f1e8] shadow-sm"
                    : "bg-transparent text-muted-foreground hover:text-foreground"
                }`}
              >
                <span>📋</span>
                <span>Jadval</span>
              </button>
            </div>

            <span className="inline-flex items-center gap-2 rounded-full border border-[#d6e4d8] bg-[#e9f3eb] px-3 py-1.5 text-[10px] font-bold text-[#397252]">
              <span className="h-2 w-2 rounded-full bg-[#397252] animate-pulse" />
              Live · {items.length}
            </span>
            <button
              type="button"
              onClick={() => setShowManual((v) => !v)}
              className="wm-btn text-xs"
            >
              + {t.manualOrderCreate}
            </button>
          </div>
        }
      />

      {showManual && (
        <ManualOrderModal
          admins={admins}
          onClose={() => setShowManual(false)}
          onCreated={(oid) => {
            setShowManual(false);
            navigate(`/admin/orders/${oid}`);
          }}
        />
      )}

      {/* Filter Bar */}
      <div className="rounded-2xl border border-border bg-card p-4 grid grid-cols-1 md:grid-cols-5 gap-3">
        <div>
          <label htmlFor="ord-q" className="wm-label">
            {t.search}
          </label>
          <input
            id="ord-q"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="WM..., ism, tel, @username"
            className="wm-input"
          />
        </div>
        <div>
          <label htmlFor="ord-st" className="wm-label">
            Holati
          </label>
          <select
            id="ord-st"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="wm-input"
          >
            <option value="">Barchasi</option>
            {ALL_STATUSES.map((st) => (
              <option key={st} value={st}>
                {getStatusLabel(st, lang)}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="ord-adm" className="wm-label">
            Admin
          </label>
          <select
            id="ord-adm"
            value={adminId}
            onChange={(e) => setAdminId(e.target.value)}
            className="wm-input"
          >
            <option value="">Barchasi</option>
            {admins.map((a) => (
              <option key={a.id} value={a.id}>
                {a.full_name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="ord-df" className="wm-label">
            Sanadan
          </label>
          <input
            id="ord-df"
            type="date"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
            className="wm-input"
          />
        </div>
        <div>
          <label htmlFor="ord-dt" className="wm-label">
            Sanagacha
          </label>
          <input
            id="ord-dt"
            type="date"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
            className="wm-input"
          />
        </div>
      </div>

      {loading ? (
        <SkeletonList count={4} />
      ) : items.length === 0 ? (
        <EmptyState text="Buyurtmalar topilmadi" />
      ) : viewMode === "kanban" ? (
        /* Modern SaaS Kanban Board */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 items-start overflow-x-auto pb-4">
          {[
            {
              id: "new",
              title: "Yangi so‘rovlar",
              match: ["new"],
              color: "from-blue-500/10 via-indigo-500/5 to-transparent",
              border: "border-blue-300/80",
              badge: "bg-blue-100 text-blue-900 border-blue-200",
              nextStatus: "pending_payment",
              nextLabel: "To‘lov kutilmoqda →",
              icon: "📥",
            },
            {
              id: "pending_payment",
              title: "To‘lov kutilmoqda",
              match: ["pending_payment", "confirmed"],
              color: "from-amber-500/10 via-yellow-500/5 to-transparent",
              border: "border-amber-300/80",
              badge: "bg-amber-100 text-amber-900 border-amber-200",
              nextStatus: "in_transit",
              nextLabel: "Xitoydan yo‘lda →",
              icon: "⏳",
            },
            {
              id: "in_transit",
              title: "Xitoydan yo‘lda (Kargo)",
              match: ["in_transit", "paid", "ordered_china"],
              color: "from-purple-500/10 via-violet-500/5 to-transparent",
              border: "border-purple-300/80",
              badge: "bg-purple-100 text-purple-900 border-purple-200",
              nextStatus: "delivering",
              nextLabel: "Yetkazishga berish →",
              icon: "✈️",
            },
            {
              id: "delivering",
              title: "Yetkazilmoqda (Pochta)",
              match: ["delivering"],
              color: "from-orange-500/10 via-amber-500/5 to-transparent",
              border: "border-orange-300/80",
              badge: "bg-orange-100 text-orange-900 border-orange-200",
              nextStatus: "delivered",
              nextLabel: "Topshirildi ✓",
              icon: "🚚",
            },
            {
              id: "delivered",
              title: "Bajarildi & Topshirildi",
              match: ["delivered"],
              color: "from-emerald-500/10 via-teal-500/5 to-transparent",
              border: "border-emerald-300/80",
              badge: "bg-emerald-100 text-emerald-900 border-emerald-200",
              nextStatus: null,
              nextLabel: null,
              icon: "✅",
            },
          ].map((col) => {
            const colOrders = items.filter((o) => col.match.includes(o.status));
            const colSum = colOrders.reduce(
              (acc, o) => acc + (Number(o.total) || 0),
              0
            );

            return (
              <div
                key={col.id}
                className={`flex flex-col rounded-2xl border ${col.border} bg-gradient-to-b ${col.color} bg-white/70 p-3.5 shadow-sm min-w-[240px]`}
              >
                {/* Column Header */}
                <div className="mb-2.5 flex items-center justify-between border-b border-border/70 pb-2">
                  <div className="flex items-center gap-1.5 font-bold text-xs text-foreground">
                    <span>{col.icon}</span>
                    <span className="line-clamp-1">{col.title}</span>
                  </div>
                  <span
                    className={`rounded-full border px-2 py-0.5 text-[10px] font-extrabold ${col.badge}`}
                  >
                    {colOrders.length}
                  </span>
                </div>

                {/* Column Total Sum */}
                <div className="mb-3 flex items-center justify-between text-[11px] font-semibold text-muted-foreground">
                  <span>Jami qiymat:</span>
                  <span className="font-extrabold text-[#172641]">
                    {formatPrice(colSum)}
                  </span>
                </div>

                {/* Cards in Column */}
                <div className="space-y-3">
                  {colOrders.length === 0 ? (
                    <div className="rounded-xl border border-dashed border-border/80 bg-white/40 p-5 text-center text-xs text-muted-foreground">
                      Hozircha buyurtma yo‘q
                    </div>
                  ) : (
                    colOrders.map((o) => (
                      <div
                        key={o.id}
                        className="group relative flex flex-col justify-between rounded-xl border border-border/80 bg-card p-3.5 shadow-xs transition-all duration-200 hover:-translate-y-0.5 hover:border-[#c5a676] hover:shadow-md"
                      >
                        <div>
                          {/* Card Top: Code & Date */}
                          <div className="flex items-center justify-between">
                            <Link
                              to={`/admin/orders/${o.id}`}
                              className="font-extrabold text-xs text-foreground no-underline hover:text-[#8a6c43] hover:underline"
                            >
                              {o.code}
                            </Link>
                            <span className="text-[10px] text-muted-foreground">
                              {o.created_at ? o.created_at.split("T")[0] : ""}
                            </span>
                          </div>

                          {/* Customer Details */}
                          <div className="mt-2 text-xs">
                            <div className="font-bold text-foreground">{o.name}</div>
                            <div className="mt-0.5 flex flex-wrap items-center gap-1.5 text-[11px] text-muted-foreground">
                              {o.phone && (
                                <a
                                  href={`tel:${o.phone}`}
                                  className="text-foreground hover:underline"
                                  onClick={(e) => e.stopPropagation()}
                                >
                                  📞 {o.phone}
                                </a>
                              )}
                              {o.tg_username && (
                                <a
                                  href={`https://t.me/${o.tg_username.replace("@", "")}`}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="text-[#2aabee] hover:underline font-semibold"
                                  onClick={(e) => e.stopPropagation()}
                                >
                                  @{o.tg_username.replace("@", "")}
                                </a>
                              )}
                            </div>
                            <div className="mt-1 text-[10px] text-muted-foreground">
                              📍 {o.city || "Toshkent"} {o.address ? `· ${o.address}` : ""}
                            </div>
                          </div>

                          {/* Items count / preview */}
                          {Array.isArray(o.items) && o.items.length > 0 && (
                            <div className="mt-2.5 rounded-lg bg-[#faf7f0] p-2 text-[10.5px] border border-[#e8dfcf]/60">
                              <div className="font-semibold text-foreground line-clamp-1">
                                {o.items
                                  .map((it: any) => it.product_name || it.name)
                                  .join(", ")}
                              </div>
                              <div className="text-[9.5px] text-muted-foreground">
                                {o.items.length} ta mahsulot
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Card Footer: Price & One-click Next Status */}
                        <div className="mt-3 pt-2.5 border-t border-border/70">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                              Jami:
                            </span>
                            <span className="font-extrabold text-xs text-[#172641]">
                              {formatPrice(o.total)}
                            </span>
                          </div>

                          <div className="flex items-center gap-1.5">
                            {col.nextStatus && (
                              <button
                                type="button"
                                onClick={() =>
                                  quickChangeStatus(o.id, col.nextStatus!)
                                }
                                className="flex-1 rounded-lg bg-[#172641] py-1.5 px-2 text-[10px] font-bold text-[#faf7f2] transition hover:bg-[#23385e] active:scale-95 cursor-pointer border-0"
                              >
                                {col.nextLabel}
                              </button>
                            )}
                            <a
                              href={`/api/admin/ops/label/${o.id}`}
                              target="_blank"
                              rel="noreferrer"
                              className="rounded-lg border border-border bg-[#faf7f0] p-1.5 text-[10px] text-foreground no-underline hover:bg-[#efe9dc] transition"
                              title="Pochta nakladnoyini chop etish"
                            >
                              🖨
                            </a>
                            <Link
                              to={`/admin/orders/${o.id}`}
                              className="rounded-lg border border-border bg-[#faf7f0] py-1.5 px-2 text-[10px] font-bold text-foreground no-underline hover:bg-[#efe9dc] transition"
                            >
                              Batafsil
                            </Link>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* Traditional Table View */
        <div className="overflow-hidden rounded-2xl border border-border bg-card">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[850px] text-left">
              <thead className="bg-[#f6f2e9] text-[9px] font-bold uppercase tracking-[.12em] text-muted-foreground">
                <tr>
                  <th className="px-4 py-3 w-10">
                    <input
                      type="checkbox"
                      checked={items.length > 0 && selected.length === items.length}
                      onChange={toggleSelectAll}
                      className="h-4 w-4 rounded accent-[#172641] cursor-pointer"
                    />
                  </th>
                  <th className="px-4 py-3">Order</th>
                  <th className="px-4 py-3">Customer</th>
                  <th className="px-4 py-3">Pochta manzili</th>
                  <th className="px-4 py-3">Admin</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Total</th>
                  <th className="px-4 py-3 text-center">Pochta</th>
                </tr>
              </thead>
              <tbody>
                {items.map((o) => {
                  const isChecked = selected.includes(o.id);

                  return (
                    <tr
                      key={o.id}
                      onClick={() => navigate(`/admin/orders/${o.id}`)}
                      className={`cursor-pointer border-t border-border/70 transition hover:bg-[#f9f6ef] ${
                        isChecked ? "bg-[#faf5ea]" : ""
                      }`}
                    >
                      <td
                        className="px-4 py-3.5"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelected((prev) => [...prev, o.id]);
                            } else {
                              setSelected((prev) =>
                                prev.filter((id) => id !== o.id)
                              );
                            }
                          }}
                          className="h-4 w-4 rounded accent-[#172641] cursor-pointer"
                        />
                      </td>
                      <td className="px-4 py-3.5">
                        <Link
                          to={`/admin/orders/${o.id}`}
                          onClick={(e) => e.stopPropagation()}
                          className="text-[12px] font-extrabold text-foreground no-underline hover:underline"
                        >
                          {o.code}
                        </Link>
                        <div className="text-[10px] text-muted-foreground">
                          {o.created_at || ""}
                        </div>
                      </td>
                      <td className="px-4 py-3.5">
                        <div className="text-[12px] font-semibold">{o.name}</div>
                        <div className="text-[10px] text-muted-foreground">
                          {o.phone || "—"}{" "}
                          {o.tg_username ? `· @${o.tg_username}` : ""}
                        </div>
                      </td>
                      <td className="px-4 py-3.5 text-[11px]">
                        <div>{o.city || "—"}</div>
                        <div className="text-[10px] text-muted-foreground">
                          📮 Pochta (BTS/EMU)
                        </div>
                      </td>
                      <td className="px-4 py-3.5 text-[11px] font-semibold">
                        {o.admin || "—"}
                      </td>
                      <td className="px-4 py-3.5">
                        <StatusBadge status={o.status} />
                      </td>
                      <td className="px-4 py-3.5 text-right text-[12px] font-extrabold">
                        {formatPrice(o.total)}
                      </td>
                      <td
                        className="px-4 py-3.5 text-center"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <a
                          href={`/api/admin/ops/label/${o.id}`}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 rounded-lg border border-[#172641]/20 bg-[#faf8f3] px-2.5 py-1 text-[10px] font-bold text-[#172641] no-underline hover:bg-[#172641] hover:text-[#f4efe5] transition"
                          title="Pochta nakladnoyini chop etish (BTS/EMU)"
                        >
                          🖨 Nakladnoy
                        </a>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Floating Bulk Status Action Bar */}
      {selected.length > 0 && (
        <div className="sticky bottom-4 z-20 mx-auto flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-[#d6bd92] bg-[#172641] p-4 text-[#f4efe5] shadow-2xl backdrop-blur-md">
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-[#d6bd92] font-bold text-xs text-[#172641]">
              {selected.length}
            </span>
            <span className="text-xs font-bold">
              buyurtma tanlandi (Kargo partiya boshqaruvi)
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <select
              value={bulkStatus}
              onChange={(e) => setBulkStatus(e.target.value)}
              className="h-9 rounded-xl border border-white/20 bg-white/10 px-3 text-xs font-bold text-white outline-none focus:bg-[#172641]"
            >
              <option value="ordered_china" className="text-black">
                🇨🇳 Xitoyda buyurtma berildi (ordered_china)
              </option>
              <option value="china_warehouse" className="text-black">
                🏢 Xitoy omborida (china_warehouse)
              </option>
              <option value="in_transit" className="text-black">
                ✈️ Yo‘lda kargo (in_transit)
              </option>
              <option value="in_uz" className="text-black">
                🇺🇿 O‘zbekistonga yetib keldi (in_uz)
              </option>
              <option value="delivered" className="text-black">
                📮 Pochtaga topshirildi / Yetkazildi (delivered)
              </option>
              <option value="paid" className="text-black">
                ✓ To‘langan (paid)
              </option>
            </select>

            <input
              value={bulkTracking}
              onChange={(e) => setBulkTracking(e.target.value)}
              placeholder="Trek-kod (ixtiyoriy)..."
              className="h-9 w-44 rounded-xl border border-white/20 bg-white/10 px-3 text-xs font-mono text-white placeholder:text-white/50 outline-none"
            >
            </input>

            <button
              type="button"
              disabled={bulkLoading}
              onClick={handleBulkStatus}
              className="h-9 rounded-xl bg-[#d6bd92] px-4 text-xs font-extrabold text-[#172641] transition hover:bg-white active:scale-95 disabled:opacity-50 border-0 cursor-pointer"
            >
              {bulkLoading ? "Yangilanmoqda..." : "Ommaviy statusni yangilash"}
            </button>

            <button
              type="button"
              onClick={() => setSelected([])}
              className="h-9 rounded-xl border border-white/20 bg-transparent px-3 text-xs text-white/70 hover:text-white border-0 cursor-pointer"
            >
              Bekor
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function ManualOrderModal({
  admins,
  onClose,
  onCreated,
}: {
  admins: any[];
  onClose: () => void;
  onCreated: (oid: number) => void;
}) {
  const { t } = useLang();
  const { toast } = useToast();
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("+998");
  const [tgUsername, setTgUsername] = useState("");
  const [city, setCity] = useState("Toshkent");
  const [address, setAddress] = useState("");
  const [delivery, setDelivery] = useState("courier");
  const [variantId, setVariantId] = useState("");
  const [qty, setQty] = useState(1);
  const [assignedAdminId, setAssignedAdminId] = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await adminFetch("/api/admin/orders", {
        method: "POST",
        body: JSON.stringify({
          name,
          phone,
          tg_username: tgUsername,
          city,
          address,
          delivery,
          assigned_admin_id: assignedAdminId ? Number(assignedAdminId) : null,
          items: [{ variant_id: Number(variantId), qty: Number(qty) }],
        }),
      });
      toast(t.savedToast);
      onCreated(res.id);
    } catch (err: any) {
      toast(err.message, "error");
    }
  };

  return (
    <form
      onSubmit={submit}
      className="rounded-2xl border border-border bg-card p-5 space-y-4 rise-in"
    >
      <div className="flex justify-between items-center">
        <h3 className="text-[16px] font-extrabold">{t.manualOrderCreate}</h3>
        <button
          type="button"
          onClick={onClose}
          className="wm-btn-outline text-xs"
        >
          {t.close}
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div>
          <label htmlFor="mo-name" className="wm-label">
            Mijoz ismi *
          </label>
          <input
            id="mo-name"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="wm-input"
          />
        </div>
        <div>
          <label htmlFor="mo-phone" className="wm-label">
            Telefon *
          </label>
          <input
            id="mo-phone"
            required
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            className="wm-input"
          />
        </div>
        <div>
          <label htmlFor="mo-tg" className="wm-label">
            Telegram username
          </label>
          <input
            id="mo-tg"
            value={tgUsername}
            onChange={(e) => setTgUsername(e.target.value)}
            className="wm-input"
          />
        </div>
        <div>
          <label htmlFor="mo-city" className="wm-label">
            Shahar
          </label>
          <input
            id="mo-city"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            className="wm-input"
          />
        </div>
        <div>
          <label htmlFor="mo-addr" className="wm-label">
            Manzil
          </label>
          <input
            id="mo-addr"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            className="wm-input"
          />
        </div>
        <div>
          <label htmlFor="mo-del" className="wm-label">
            Yetkazish
          </label>
          <select
            id="mo-del"
            value={delivery}
            onChange={(e) => setDelivery(e.target.value)}
            className="wm-input"
          >
            <option value="courier">Kuryer</option>
            <option value="pickup">Olib ketish</option>
          </select>
        </div>
        <div>
          <label htmlFor="mo-vid" className="wm-label">
            Variant ID *
          </label>
          <input
            id="mo-vid"
            type="number"
            required
            value={variantId}
            onChange={(e) => setVariantId(e.target.value)}
            className="wm-input"
          />
        </div>
        <div>
          <label htmlFor="mo-qty" className="wm-label">
            Soni *
          </label>
          <input
            id="mo-qty"
            type="number"
            min={1}
            value={qty}
            onChange={(e) => setQty(Number(e.target.value))}
            className="wm-input"
          />
        </div>
        <div>
          <label htmlFor="mo-adm" className="wm-label">
            Admin
          </label>
          <select
            id="mo-adm"
            value={assignedAdminId}
            onChange={(e) => setAssignedAdminId(e.target.value)}
            className="wm-input"
          >
            <option value="">Avtomatik (Round-robin)</option>
            {admins.map((a) => (
              <option key={a.id} value={a.id}>
                {a.full_name}
              </option>
            ))}
          </select>
        </div>
      </div>
      <button type="submit" className="wm-btn">
        {t.save}
      </button>
    </form>
  );
}

export function OrderDetailPage() {
  const { id } = useParams();
  const { t, lang } = useLang();
  const { toast } = useToast();
  const [order, setOrder] = useState<any>(null);
  const [admins, setAdmins] = useState<any[]>([]);
  const [status, setStatus] = useState("");
  const [tracking, setTracking] = useState("");
  const [note, setNote] = useState("");
  const [paidAmount, setPaidAmount] = useState(0);
  const [assignedId, setAssignedId] = useState<string>("");

  const load = () => {
    Promise.all([
      adminFetch(`/api/admin/orders/${id}`),
      adminFetch("/api/admin/orders/admins"),
    ])
      .then(([o, adms]) => {
        setOrder(o);
        setAdmins(adms);
        setStatus(o.status);
        setTracking(o.tracking || "");
        setNote(o.internal_note || "");
        setPaidAmount(o.paid_amount || 0);
        setAssignedId(o.assigned_admin_id ? String(o.assigned_admin_id) : "");
      })
      .catch((e) => toast(e.message, "error"));
  };

  useEffect(() => {
    load();
  }, [id]);

  if (!order) return <SkeletonList count={3} />;

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const updated = await adminFetch(`/api/admin/orders/${id}`, {
        method: "PATCH",
        body: JSON.stringify({
          status,
          tracking,
          internal_note: note,
          paid_amount: Number(paidAmount),
          assigned_admin_id: assignedId ? Number(assignedId) : null,
        }),
      });
      setOrder(updated);
      toast(t.savedToast);
    } catch (err: any) {
      toast(err.message, "error");
    }
  };

  const resend = async () => {
    try {
      const updated = await adminFetch(`/api/admin/orders/${id}/resend`, {
        method: "POST",
      });
      setOrder(updated);
      toast("Xabar navbatga qo'shildi");
    } catch (err: any) {
      toast(err.message, "error");
    }
  };

  return (
    <div className="space-y-6">
      <div className="mb-2">
        <Link
          to="/admin/orders"
          className="inline-flex items-center gap-1.5 text-xs font-bold text-muted-foreground hover:text-foreground no-underline"
        >
          ← Buyurtmalarga qaytish
        </Link>
      </div>

      <PageHeader
        eyebrow="Buyurtma tafsiloti"
        title={`Buyurtma ${order.code}`}
        detail={`${order.name} · ${order.phone || "—"}`}
        action={
          <div className="flex flex-wrap items-center gap-2.5">
            <StatusBadge status={order.status} />
            <a
              href={`/api/admin/ops/label/${order.id}`}
              target="_blank"
              rel="noreferrer"
              className="wm-btn text-xs py-1.5 px-3.5 no-underline inline-flex items-center gap-1.5 shadow-sm"
              title="Pochta orqali yuborish uchun tayyor qog'oz varaqasi"
            >
              🖨 Pochta nakladnoyi (BTS / EMU)
            </a>
          </div>
        }
      />

      {/* Replit 2-Column Order Detail Layout */}
      <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1fr_340px]">
        {/* Left Column: Items, Delivery, History */}
        <div className="space-y-5">
          <section className="overflow-hidden rounded-2xl border border-border bg-card">
            <div className="border-b border-border px-5 py-4">
              <h2 className="text-[14px] font-extrabold">Buyurtma tarkibi</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#f6f2e9] text-[9px] font-bold uppercase tracking-[.12em] text-muted-foreground">
                  <tr>
                    <th className="px-5 py-3">Mahsulot</th>
                    <th className="px-4 py-3">O‘lcham / Rang</th>
                    <th className="px-4 py-3">Soni</th>
                    <th className="px-5 py-3 text-right">Summa</th>
                  </tr>
                </thead>
                <tbody>
                  {order.items.map((it: any) => (
                    <tr key={it.id} className="border-t border-border/70">
                      <td className="px-5 py-3.5 font-bold">{it.name}</td>
                      <td className="px-4 py-3.5">
                        <span className="rounded-md bg-muted px-2 py-1 text-[10px] font-semibold">
                          {it.size} · {it.color}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 font-semibold">{it.qty}</td>
                      <td className="px-5 py-3.5 text-right font-extrabold">
                        {formatPrice(it.price * it.qty)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="flex items-center justify-between border-t border-border bg-[#faf8f3] px-5 py-4">
              <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
                Jami to‘lov{" "}
                {order.discount > 0
                  ? `(Chegirma: ${formatPrice(order.discount)})`
                  : ""}
              </span>
              <span className="font-display text-[24px] font-medium">
                {formatPrice(order.total)}
              </span>
            </div>
          </section>

          <section className="rounded-2xl border border-border bg-card p-5">
            <h2 className="mb-3 text-[14px] font-extrabold">
              Yetkazib berish manzili
            </h2>
            <dl className="grid grid-cols-1 gap-3 text-xs sm:grid-cols-2">
              <div>
                <dt className="text-[10px] uppercase tracking-wider text-muted-foreground">
                  Shahar
                </dt>
                <dd className="mt-0.5 font-semibold">{order.city || "—"}</dd>
              </div>
              <div>
                <dt className="text-[10px] uppercase tracking-wider text-muted-foreground">
                  Yetkazish turi
                </dt>
                <dd className="mt-0.5 font-semibold">
                  {order.delivery === "pickup" ? t.pickup : t.courier}
                </dd>
              </div>
              <div className="sm:col-span-2">
                <dt className="text-[10px] uppercase tracking-wider text-muted-foreground">
                  Manzil
                </dt>
                <dd className="mt-0.5 font-semibold">{order.address || "—"}</dd>
              </div>
              <div className="sm:col-span-2">
                <dt className="text-[10px] uppercase tracking-wider text-muted-foreground">
                  Mijoz izohi
                </dt>
                <dd className="mt-0.5 font-semibold">{order.comment || "—"}</dd>
              </div>
            </dl>
          </section>

          <section className="rounded-2xl border border-border bg-card p-5 space-y-2">
            <h2 className="text-[14px] font-extrabold">{t.statusHistory}</h2>
            {(order.history || []).map((h: any, i: number) => (
              <div
                key={i}
                className="flex items-center justify-between border-b border-border/60 py-2 last:border-0 text-xs"
              >
                <span className="font-bold">
                  {getStatusLabel(h.status, lang)}
                </span>
                <span className="text-muted-foreground">
                  {h.by} · {h.at}
                </span>
              </div>
            ))}
          </section>

          {order.receipt_photo && (
            <section className="rounded-2xl border border-border bg-card p-5 space-y-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <h2 className="text-[14px] font-extrabold">
                    💳 Yuklangan to'lov cheki (Avans)
                  </h2>
                  <p className="text-xs text-muted-foreground">
                    Kutilayotgan avans: {formatPrice(order.advance_amount || 0)}
                  </p>
                </div>
                {order.status !== "paid" && order.status !== "delivered" && (
                  <button
                    type="button"
                    onClick={async () => {
                      try {
                        const updated = await adminFetch(
                          `/api/admin/orders/${id}`,
                          {
                            method: "PATCH",
                            body: JSON.stringify({ status: "paid" }),
                          }
                        );
                        setOrder(updated);
                        setStatus(updated.status);
                        setPaidAmount(updated.paid_amount || 0);
                        toast("To'lov tasdiqlandi!");
                      } catch (err: any) {
                        toast(err.message, "error");
                      }
                    }}
                    className="wm-btn text-xs"
                  >
                    ✅ To'lovni tasdiqlash
                  </button>
                )}
              </div>
              <a
                href={`/uploads/${order.receipt_photo}`}
                target="_blank"
                rel="noreferrer"
                className="block max-w-sm overflow-hidden rounded-xl border border-border"
              >
                <img
                  src={`/uploads/${order.receipt_photo}`}
                  alt="To'lov cheki"
                  className="max-h-80 w-full object-contain bg-[#faf8f3]"
                />
              </a>
            </section>
          )}
        </div>

        {/* Right Aside: Update Form, Notification, Dark Navy Customer Card */}
        <aside className="space-y-4">
          <form
            onSubmit={save}
            className="rounded-2xl border border-border bg-card p-5 space-y-3.5"
          >
            <h2 className="text-[14px] font-extrabold">Buyurtmani yangilash</h2>
            <div>
              <label htmlFor="od-st" className="wm-label">
                Holati
              </label>
              <select
                id="od-st"
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                className="wm-input"
              >
                {ALL_STATUSES.map((st) => (
                  <option key={st} value={st}>
                    {getStatusLabel(st, lang)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="od-adm" className="wm-label">
                Biriktirilgan admin
              </label>
              <select
                id="od-adm"
                value={assignedId}
                onChange={(e) => setAssignedId(e.target.value)}
                className="wm-input"
              >
                <option value="">Tanlanmagan</option>
                {admins.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.full_name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="od-trk" className="wm-label">
                {t.trackingNumber}
              </label>
              <input
                id="od-trk"
                value={tracking}
                onChange={(e) => setTracking(e.target.value)}
                placeholder="CN-UZ-000123"
                className="wm-input"
              />
            </div>
            <div>
              <label htmlFor="od-paid" className="wm-label">
                To'langan summa (so'm)
              </label>
              <input
                id="od-paid"
                type="number"
                value={paidAmount}
                onChange={(e) => setPaidAmount(Number(e.target.value))}
                className="wm-input"
              />
            </div>
            <div>
              <label htmlFor="od-note" className="wm-label">
                {t.internalNote}
              </label>
              <textarea
                id="od-note"
                rows={3}
                value={note}
                onChange={(e) => setNote(e.target.value)}
                className="wm-input"
              />
            </div>
            <button type="submit" className="wm-btn w-full">
              {t.save}
            </button>
          </form>

          <section className="rounded-2xl border border-border bg-card p-5 space-y-3">
            <h2 className="text-[14px] font-extrabold">Manba va xabarnoma</h2>
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Telegram xabari</span>
              <span className="font-bold">{order.notification}</span>
            </div>
            <button
              type="button"
              onClick={resend}
              className="wm-btn-outline text-xs w-full"
            >
              {t.resendNotification} ({order.notification})
            </button>
          </section>

          <section className="rounded-2xl bg-[#172641] p-5 text-[#f4efe5]">
            <div className="text-[9px] font-bold uppercase tracking-[.18em] text-[#d6bd92]">
              Mijoz / Customer
            </div>
            <div className="mt-2 font-display text-[20px]">{order.name}</div>
            <div className="mt-2 space-y-1 text-xs text-white/75">
              <div>Tel: {order.phone || "Kiritilmagan"}</div>
              {order.tg_username && <div>Telegram: @{order.tg_username}</div>}
            </div>
            {order.tg_username && (
              <a
                href={`https://t.me/${order.tg_username.replace(/^@/, "")}`}
                target="_blank"
                rel="noreferrer"
                className="mt-4 inline-flex items-center gap-1.5 rounded-lg bg-[#c5a776] px-3 py-2 text-[11px] font-bold text-[#172641] no-underline"
              >
                Telegramda yozish ↗
              </a>
            )}
          </section>
        </aside>
      </div>
    </div>
  );
}

// ---------------- 5. CUSTOMERS ----------------
export function CustomersPage() {
  const { t, lang } = useLang();
  const { toast } = useToast();
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [detail, setDetail] = useState<any>(null);
  const [msgText, setMsgText] = useState("");

  useEffect(() => {
    setLoading(true);
    adminFetch(`/api/admin/customers?q=${encodeURIComponent(q)}`)
      .then((res) => setItems(res.items || []))
      .catch((e) => toast(e.message, "error"))
      .finally(() => setLoading(false));
  }, [q]);

  const sendMsg = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!detail) return;
    try {
      await adminFetch(`/api/admin/customers/${detail.id}/message`, {
        method: "POST",
        body: JSON.stringify({ text: msgText }),
      });
      setMsgText("");
      toast("Xabar navbatga qo'shildi");
    } catch (err: any) {
      toast(err.message, "error");
    }
  };

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="CRM · Customers"
        title="Mijozlar bazasi"
        detail="Mini App va bot orqali ro‘yxatdan o‘tgan xaridlar tarixi."
      />

      <div>
        <label htmlFor="cust-q" className="wm-label">
          {t.search}
        </label>
        <input
          id="cust-q"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder={t.searchPlaceholder}
          className="wm-input max-w-sm"
        />
      </div>

      {detail && (
        <div className="rounded-2xl border border-border bg-card p-5 space-y-4 rise-in">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-[16px] font-extrabold">
                {detail.name} — Jami xarid: {formatPrice(detail.total_spent)}
              </h2>
              <p className="text-xs text-muted-foreground">
                {detail.phone || "—"}{" "}
                {detail.username ? `· @${detail.username}` : ""}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Link
                to="/admin/crm"
                className="wm-btn text-xs py-1.5 px-3 no-underline inline-flex items-center gap-1"
              >
                <span>📊 CRM Dosye & Razmerlar ↗</span>
              </Link>
              <button
                type="button"
                onClick={() => setDetail(null)}
                className="wm-btn-outline text-xs"
              >
                {t.close}
              </button>
            </div>
          </div>
          <form onSubmit={sendMsg} className="flex gap-2 items-end">
            <div className="flex-1">
              <label htmlFor="cust-msg" className="wm-label">
                {t.sendMessage}
              </label>
              <input
                id="cust-msg"
                required
                value={msgText}
                onChange={(e) => setMsgText(e.target.value)}
                className="wm-input"
              />
            </div>
            <button type="submit" className="wm-btn text-xs">
              Yuborish
            </button>
          </form>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {(detail.order_list || []).map((o: any) => (
              <Link
                key={o.id}
                to={`/admin/orders/${o.id}`}
                className="flex items-center justify-between rounded-xl border border-border bg-[#faf8f3] px-3 py-2 text-xs text-foreground no-underline hover:border-primary"
              >
                <div>
                  <div className="font-extrabold">{o.code}</div>
                  <div className="text-[10px] text-muted-foreground">
                    {getStatusLabel(o.status, lang)}
                  </div>
                </div>
                <span className="font-bold">{formatPrice(o.total)}</span>
              </Link>
            ))}
          </div>
        </div>
      )}

      {loading ? (
        <SkeletonList count={4} />
      ) : items.length === 0 ? (
        <EmptyState text="Mijozlar topilmadi" />
      ) : (
        <div className="overflow-hidden rounded-2xl border border-border bg-card">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[700px] text-left">
              <thead className="bg-[#f6f2e9] text-[9px] font-bold uppercase tracking-[.12em] text-muted-foreground">
                <tr>
                  <th className="px-5 py-3">Mijoz</th>
                  <th className="px-4 py-3">Telefon / Telegram</th>
                  <th className="px-4 py-3">Buyurtmalar</th>
                  <th className="px-4 py-3">Xaridlar</th>
                  <th className="px-5 py-3 text-right">Aloqa</th>
                </tr>
              </thead>
              <tbody>
                {items.map((c) => (
                  <tr
                    key={c.id}
                    onClick={async () => {
                      const d = await adminFetch(
                        `/api/admin/customers/${c.id}`
                      );
                      setDetail(d);
                    }}
                    className="cursor-pointer border-t border-border/70 hover:bg-[#f9f6ef]"
                  >
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-3">
                        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#f0eadd] font-display text-sm text-[#7f6a48]">
                          {(c.name || "M").slice(0, 1).toUpperCase()}
                        </div>
                        <div className="text-xs font-bold">{c.name}</div>
                      </div>
                    </td>
                    <td className="px-4 py-3.5 text-xs text-muted-foreground">
                      {c.phone || "-"}{" "}
                      {c.username ? `· @${c.username}` : ""}
                    </td>
                    <td className="px-4 py-3.5 text-xs font-bold text-primary">
                      {c.orders} ta
                    </td>
                    <td className="px-4 py-3.5 text-xs font-extrabold">
                      {formatPrice(c.total_spent)}
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <span className="rounded-lg border border-border px-2.5 py-1.5 text-[11px] font-bold">
                        Tarix va Xabar →
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// ---------------- 6. PROMOTIONS & BROADCAST ----------------
export function PromotionsPage() {
  const { t } = useLang();
  const { toast } = useToast();
  const [promos, setPromos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [code, setCode] = useState("");
  const [percent, setPercent] = useState(10);
  const [limit, setLimit] = useState(0);
  const [expires, setExpires] = useState("");
  const [bText, setBText] = useState("");
  const [bPhoto, setBPhoto] = useState<File | null>(null);
  const [bPreview, setBPreview] = useState("");
  const [delId, setDelId] = useState<number | null>(null);

  const load = () => {
    setLoading(true);
    adminFetch("/api/admin/promocodes")
      .then(setPromos)
      .catch((e) => toast(e.message, "error"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const addPromo = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await adminFetch("/api/admin/promocodes", {
        method: "POST",
        body: JSON.stringify({
          code,
          percent: Number(percent),
          usage_limit: Number(limit),
          expires_at: expires || null,
          active: true,
        }),
      });
      setCode("");
      toast(t.savedToast);
      load();
    } catch (err: any) {
      toast(err.message, "error");
    }
  };

  const sendBroadcast = async (e: React.FormEvent) => {
    e.preventDefault();
    const fd = new FormData();
    fd.append("text", bText);
    if (bPhoto) fd.append("photo", bPhoto);
    try {
      const r = await adminFetch("/api/admin/broadcast", {
        method: "POST",
        body: fd,
      });
      setBText("");
      setBPhoto(null);
      setBPreview("");
      toast(`${r.queued} ta mijozga navbatga qo'shildi`);
    } catch (err: any) {
      toast(err.message, "error");
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Kampaniyalar · Promotions"
        title="Aksiyalar va xabarnomalar"
        detail="Chegirma promo-kodlari va mijozlarga ommaviy Telegram xabarlari."
      />

      {/* Replit Dark Navy Broadcast Banner */}
      <div className="rounded-2xl bg-[#172641] p-6 text-[#f4efe5]">
        <div className="max-w-xl">
          <div className="text-[10px] font-bold uppercase tracking-[.2em] text-[#d6bd92]">
            Mijozlar bilan aloqa
          </div>
          <h2 className="mt-1.5 font-display text-[26px]">
            Telegram orqali yangilik ulashing.
          </h2>
          <p className="mt-1.5 text-xs text-white/65">
            Yangi kolleksiya yoki chegirma haqida barcha faol mijozlarga rasm va
            matnli xabar yuboring.
          </p>
        </div>
      </div>

      {/* Promo Code Form */}
      <form
        onSubmit={addPromo}
        className="rounded-2xl border border-border bg-card p-5 grid grid-cols-1 md:grid-cols-5 gap-3 items-end"
      >
        <div>
          <label htmlFor="pr-code" className="wm-label">
            Kod *
          </label>
          <input
            id="pr-code"
            required
            value={code}
            onChange={(e) => setCode(e.target.value.toUpperCase())}
            placeholder="WITHMORE10"
            className="wm-input"
          />
        </div>
        <div>
          <label htmlFor="pr-pct" className="wm-label">
            Foiz (%)
          </label>
          <input
            id="pr-pct"
            type="number"
            min={1}
            max={90}
            value={percent}
            onChange={(e) => setPercent(Number(e.target.value))}
            className="wm-input"
          />
        </div>
        <div>
          <label htmlFor="pr-lim" className="wm-label">
            Limit (0=cheksiz)
          </label>
          <input
            id="pr-lim"
            type="number"
            min={0}
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="wm-input"
          />
        </div>
        <div>
          <label htmlFor="pr-exp" className="wm-label">
            Muddati
          </label>
          <input
            id="pr-exp"
            type="date"
            value={expires}
            onChange={(e) => setExpires(e.target.value)}
            className="wm-input"
          />
        </div>
        <button type="submit" className="wm-btn">
          + {t.add}
        </button>
      </form>

      {/* Promo Codes Grid */}
      <div>
        <h3 className="mb-3 text-[15px] font-extrabold">Promo-kodlar</h3>
        {loading ? (
          <SkeletonList count={2} />
        ) : promos.length === 0 ? (
          <EmptyState text="Promokodlar yo'q" />
        ) : (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            {promos.map((p) => (
              <div
                key={p.id}
                className="relative overflow-hidden rounded-2xl border border-border bg-card p-5 flex flex-col justify-between"
              >
                <div className="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full border border-[#c8ac7f]/25" />
                <div>
                  <div className="flex items-center justify-between">
                    <span className="rounded-lg bg-[#172641] px-3 py-1 font-mono text-xs font-bold tracking-wider text-[#f3e7d1]">
                      {p.code}
                    </span>
                    <span className="text-[10px] font-bold text-[#397252]">
                      Faol
                    </span>
                  </div>
                  <div className="mt-4 font-display text-[32px] font-medium">
                    -{p.percent}%{" "}
                    <span className="text-sm text-muted-foreground">
                      chegirma
                    </span>
                  </div>
                  <div className="mt-2 text-[11px] text-muted-foreground">
                    Ishlatildi: {p.used_count} / {p.usage_limit || "∞"}
                  </div>
                </div>
                <div className="mt-4 pt-3 border-t border-border/70 flex justify-end">
                  <button
                    type="button"
                    onClick={() => setDelId(p.id)}
                    className="wm-btn-outline text-xs text-[#a3463c]"
                  >
                    {t.delete}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Broadcast Form */}
      <form
        onSubmit={sendBroadcast}
        className="rounded-2xl border border-border bg-card p-6 space-y-4"
      >
        <h2 className="text-[15px] font-extrabold">{t.broadcastTitle}</h2>
        <div>
          <label htmlFor="br-text" className="wm-label">
            Xabar matni *
          </label>
          <textarea
            id="br-text"
            required
            rows={3}
            value={bText}
            onChange={(e) => setBText(e.target.value)}
            className="wm-input"
          />
        </div>
        <div>
          <label htmlFor="br-photo" className="wm-label">
            Rasm (ixtiyoriy)
          </label>
          <input
            id="br-photo"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={(e) => {
              const f = e.target.files?.[0] || null;
              setBPhoto(f);
              setBPreview(f ? URL.createObjectURL(f) : "");
            }}
            className="text-xs"
          />
        </div>
        {bPreview && (
          <img
            src={bPreview}
            alt="Preview"
            className="w-40 h-40 object-cover rounded-xl border border-border"
          />
        )}
        <button type="submit" className="wm-btn">
          Yuborish
        </button>
      </form>

      <ConfirmModal
        open={delId !== null}
        title={t.confirmDelete}
        onCancel={() => setDelId(null)}
        onConfirm={async () => {
          const id = delId;
          setDelId(null);
          await adminFetch(`/api/admin/promocodes/${id}`, {
            method: "DELETE",
          });
          toast(t.deletedToast);
          load();
        }}
      />
    </div>
  );
}

// ---------------- 7. TEAM (OWNER ONLY) ----------------
export function TeamPage() {
  const { t } = useLang();
  const { toast } = useToast();
  const [members, setMembers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [fullName, setFullName] = useState("");
  const [tgUser, setTgUser] = useState("");
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("admin");
  const [perms, setPerms] = useState<string[]>(["orders", "products"]);
  const [accepts, setAccepts] = useState(true);

  const load = () => {
    setLoading(true);
    adminFetch("/api/admin/team")
      .then(setMembers)
      .catch((e) => toast(e.message, "error"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const add = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await adminFetch("/api/admin/team", {
        method: "POST",
        body: JSON.stringify({
          full_name: fullName,
          tg_username: tgUser,
          login,
          password,
          role,
          permissions: perms,
          accepts_orders: accepts,
        }),
      });
      setFullName("");
      setTgUser("");
      setLogin("");
      setPassword("");
      toast(t.savedToast);
      load();
    } catch (err: any) {
      toast(err.message, "error");
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Team · Jamoa"
        title="Jamoa va ruxsatlar"
        detail="Har bir admin faqat o‘ziga kerakli bo‘limlarni ko‘radi."
      />

      <form
        onSubmit={add}
        className="rounded-2xl border border-border bg-card p-6 space-y-4"
      >
        <h2 className="text-[15px] font-extrabold">Yangi admin qo'shish</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div>
            <label htmlFor="tm-fn" className="wm-label">
              To'liq ism *
            </label>
            <input
              id="tm-fn"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="wm-input"
            />
          </div>
          <div>
            <label htmlFor="tm-tg" className="wm-label">
              @telegram_username
            </label>
            <input
              id="tm-tg"
              value={tgUser}
              onChange={(e) => setTgUser(e.target.value)}
              className="wm-input"
            />
          </div>
          <div>
            <label htmlFor="tm-lg" className="wm-label">
              Login *
            </label>
            <input
              id="tm-lg"
              required
              value={login}
              onChange={(e) => setLogin(e.target.value)}
              className="wm-input"
            />
          </div>
          <div>
            <label htmlFor="tm-pw" className="wm-label">
              Vaqtinchalik parol (kamida 10 belgi) *
            </label>
            <input
              id="tm-pw"
              type="password"
              required
              minLength={10}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="wm-input"
            />
          </div>
          <div>
            <label htmlFor="tm-rl" className="wm-label">
              Rol
            </label>
            <select
              id="tm-rl"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="wm-input"
            >
              <option value="admin">Admin</option>
              <option value="owner">Owner</option>
            </select>
          </div>
          <div className="flex items-center pt-5">
            <label className="flex items-center gap-2 text-xs font-bold">
              <input
                type="checkbox"
                checked={accepts}
                onChange={(e) => setAccepts(e.target.checked)}
                className="accent-[#172641]"
              />
              Buyurtma qabul qiladi
            </label>
          </div>
        </div>
        <div className="space-y-2">
          <div className="wm-label">Ruxsatlar</div>
          <div className="flex flex-wrap gap-2">
            {ALL_PERMS.map((p) => {
              const checked = perms.includes(p);
              return (
                <label
                  key={p}
                  className={`flex cursor-pointer items-center gap-2 rounded-lg border px-3 py-2 text-xs font-semibold transition ${
                    checked
                      ? "border-[#aa8a5e] bg-[#f6efe1]"
                      : "border-border bg-card"
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={(e) =>
                      setPerms((prev) =>
                        e.target.checked
                          ? [...prev, p]
                          : prev.filter((x) => x !== p)
                      )
                    }
                    className="accent-[#aa8a5e]"
                  />
                  {p}
                </label>
              );
            })}
          </div>
        </div>
        <button type="submit" className="wm-btn">
          + {t.add}
        </button>
      </form>

      {loading ? (
        <SkeletonList count={3} />
      ) : (
        <div className="overflow-hidden rounded-2xl border border-border bg-card">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] text-left">
              <thead className="bg-[#f6f2e9] text-[9px] font-bold uppercase tracking-[.12em] text-muted-foreground">
                <tr>
                  <th className="px-5 py-3">Admin</th>
                  <th className="px-4 py-3">Rol</th>
                  <th className="px-4 py-3">Ruxsatlar</th>
                  <th className="px-4 py-3">Holat</th>
                  <th className="px-5 py-3 text-right">Amallar</th>
                </tr>
              </thead>
              <tbody>
                {members.map((m) => (
                  <tr
                    key={m.id}
                    className={`border-t border-border/70 ${
                      m.blocked ? "opacity-55" : ""
                    }`}
                  >
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-3">
                        <div className="flex h-9 w-9 items-center justify-center rounded-full border border-[#a58b65] font-display text-[13px] text-[#806a48]">
                          {(m.full_name || "A").slice(0, 1).toUpperCase()}
                        </div>
                        <div>
                          <div className="text-[12px] font-bold">
                            {m.full_name} ({m.login})
                          </div>
                          <div className="text-[10px] text-muted-foreground">
                            @{m.tg_username || "-"} · So'nggi kirish:{" "}
                            {m.last_login || "-"}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3.5">
                      <span
                        className={`rounded-full px-2.5 py-1 text-[9px] font-bold ${
                          m.role === "owner"
                            ? "bg-[#172641] text-[#e9dcc3]"
                            : "bg-[#eee8dc] text-[#6f5e43]"
                        }`}
                      >
                        {m.role === "owner" ? "Ega" : "Admin"}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-[11px] text-muted-foreground">
                      {m.role === "owner"
                        ? "Barcha bo‘limlar"
                        : (m.permissions || []).join(", ") || "—"}
                    </td>
                    <td className="px-4 py-3.5">
                      <span
                        className={`text-[10px] font-bold ${
                          m.blocked ? "text-[#a3463c]" : "text-[#397252]"
                        }`}
                      >
                        {m.blocked ? "Bloklangan" : "Faol"}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <div className="flex flex-wrap justify-end gap-1.5">
                        <button
                          type="button"
                          onClick={async () => {
                            await adminFetch(`/api/admin/team/${m.id}`, {
                              method: "PATCH",
                              body: JSON.stringify({
                                full_name: m.full_name,
                                tg_username: m.tg_username,
                                login: m.login,
                                role: m.role,
                                permissions: m.permissions,
                                accepts_orders: !m.accepts_orders,
                              }),
                            });
                            toast(t.savedToast);
                            load();
                          }}
                          className="wm-btn-outline text-xs py-1.5 px-2.5 min-h-[34px]"
                        >
                          {m.accepts_orders
                            ? "Buyurtma qabul qiladi: Ha"
                            : "Buyurtma qabul qiladi: Yo'q"}
                        </button>
                        <button
                          type="button"
                          onClick={async () => {
                            const pw = prompt(
                              "Yangi parol (kamida 10 belgi):"
                            );
                            if (!pw) return;
                            try {
                              await adminFetch(
                                `/api/admin/team/${m.id}/reset-password`,
                                {
                                  method: "POST",
                                  body: JSON.stringify({ password: pw }),
                                }
                              );
                              toast(t.savedToast);
                            } catch (e: any) {
                              toast(e.message, "error");
                            }
                          }}
                          className="wm-btn-outline text-xs py-1.5 px-2.5 min-h-[34px]"
                        >
                          Parolni yangilash
                        </button>
                        <button
                          type="button"
                          onClick={async () => {
                            try {
                              await adminFetch(
                                `/api/admin/team/${m.id}/${
                                  m.blocked ? "unblock" : "block"
                                }`,
                                { method: "POST" }
                              );
                              load();
                            } catch (e: any) {
                              toast(e.message, "error");
                            }
                          }}
                          className="wm-btn-outline text-xs py-1.5 px-2.5 min-h-[34px] text-[#a3463c]"
                        >
                          {m.blocked ? "Blokdan chiqarish" : "Bloklash"}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// ---------------- 8. CONTENT / VITRINA (OWNER ONLY) ----------------
export function ContentPage() {
  const { t } = useLang();
  const { toast } = useToast();
  const [form, setForm] = useState<any>(null);

  useEffect(() => {
    adminFetch("/api/admin/content").then(setForm);
  }, []);

  if (!form) return <SkeletonList count={3} />;

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const updated = await adminFetch("/api/admin/content", {
        method: "PUT",
        body: JSON.stringify(form),
      });
      setForm(updated);
      toast(t.savedToast);
    } catch (err: any) {
      toast(err.message, "error");
    }
  };

  return (
    <form onSubmit={save} className="space-y-6">
      <PageHeader
        eyebrow="Storefront · Kontent"
        title="Do‘kon vitrinasi"
        detail="Mini App bosh sahifasi, “Biz haqimizda” va shartlar matnlari."
      />

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1fr_340px]">
        <div className="space-y-5">
          <section className="rounded-2xl border border-border bg-card p-6 space-y-4">
            <h2 className="text-[14px] font-extrabold">Bosh sahifa (Hero)</h2>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <label htmlFor="cnt-hu" className="wm-label">
                  Hero sarlavha (UZ)
                </label>
                <input
                  id="cnt-hu"
                  value={form.hero_title_uz || ""}
                  onChange={(e) =>
                    setForm({ ...form, hero_title_uz: e.target.value })
                  }
                  className="wm-input"
                />
              </div>
              <div>
                <label htmlFor="cnt-hr" className="wm-label">
                  Hero sarlavha (RU)
                </label>
                <input
                  id="cnt-hr"
                  value={form.hero_title_ru || ""}
                  onChange={(e) =>
                    setForm({ ...form, hero_title_ru: e.target.value })
                  }
                  className="wm-input"
                />
              </div>
              <div>
                <label htmlFor="cnt-tu" className="wm-label">
                  Hero matn (UZ)
                </label>
                <textarea
                  id="cnt-tu"
                  rows={2}
                  value={form.hero_text_uz || ""}
                  onChange={(e) =>
                    setForm({ ...form, hero_text_uz: e.target.value })
                  }
                  className="wm-input"
                />
              </div>
              <div>
                <label htmlFor="cnt-tr" className="wm-label">
                  Hero matn (RU)
                </label>
                <textarea
                  id="cnt-tr"
                  rows={2}
                  value={form.hero_text_ru || ""}
                  onChange={(e) =>
                    setForm({ ...form, hero_text_ru: e.target.value })
                  }
                  className="wm-input"
                />
              </div>
            </div>
            <div>
              <label htmlFor="cnt-hi" className="wm-label">
                Hero rasm yuklash
              </label>
              <input
                id="cnt-hi"
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={async (e) => {
                  const f = e.target.files?.[0];
                  if (!f) return;
                  const fd = new FormData();
                  fd.append("file", f);
                  const r = await adminFetch("/api/admin/content/hero-image", {
                    method: "POST",
                    body: fd,
                  });
                  setForm({ ...form, hero_image: r.hero_image });
                  toast(t.savedToast);
                }}
                className="text-xs"
              />
            </div>
          </section>

          <section className="rounded-2xl border border-border bg-card p-6 space-y-4">
            <h2 className="text-[14px] font-extrabold">Ma’lumot sahifasi</h2>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <label htmlFor="cnt-au" className="wm-label">
                  Biz haqimizda (UZ)
                </label>
                <textarea
                  id="cnt-au"
                  rows={3}
                  value={form.about_uz || ""}
                  onChange={(e) =>
                    setForm({ ...form, about_uz: e.target.value })
                  }
                  className="wm-input"
                />
              </div>
              <div>
                <label htmlFor="cnt-ar" className="wm-label">
                  Biz haqimizda (RU)
                </label>
                <textarea
                  id="cnt-ar"
                  rows={3}
                  value={form.about_ru || ""}
                  onChange={(e) =>
                    setForm({ ...form, about_ru: e.target.value })
                  }
                  className="wm-input"
                />
              </div>
              <div>
                <label htmlFor="cnt-du" className="wm-label">
                  Yetkazish qoidalari (UZ)
                </label>
                <textarea
                  id="cnt-du"
                  rows={3}
                  value={form.delivery_uz || ""}
                  onChange={(e) =>
                    setForm({ ...form, delivery_uz: e.target.value })
                  }
                  className="wm-input"
                />
              </div>
              <div>
                <label htmlFor="cnt-dr" className="wm-label">
                  Yetkazish qoidalari (RU)
                </label>
                <textarea
                  id="cnt-dr"
                  rows={3}
                  value={form.delivery_ru || ""}
                  onChange={(e) =>
                    setForm({ ...form, delivery_ru: e.target.value })
                  }
                  className="wm-input"
                />
              </div>
              <div>
                <label htmlFor="cnt-ru" className="wm-label">
                  Qaytarish qoidalari (UZ)
                </label>
                <textarea
                  id="cnt-ru"
                  rows={3}
                  value={form.returns_uz || ""}
                  onChange={(e) =>
                    setForm({ ...form, returns_uz: e.target.value })
                  }
                  className="wm-input"
                />
              </div>
              <div>
                <label htmlFor="cnt-rr" className="wm-label">
                  Qaytarish qoidalari (RU)
                </label>
                <textarea
                  id="cnt-rr"
                  rows={3}
                  value={form.returns_ru || ""}
                  onChange={(e) =>
                    setForm({ ...form, returns_ru: e.target.value })
                  }
                  className="wm-input"
                />
              </div>
            </div>
          </section>
        </div>

        {/* Right Aside: Contact & Live Preview */}
        <aside className="space-y-4">
          <section className="rounded-2xl border border-border bg-card p-5">
            <label htmlFor="cnt-cu" className="wm-label">
              Aloqa @username
            </label>
            <input
              id="cnt-cu"
              value={form.contact_username || ""}
              onChange={(e) =>
                setForm({ ...form, contact_username: e.target.value })
              }
              className="wm-input"
            />
            <p className="mt-2 text-[10px] leading-4 text-muted-foreground">
              Buyurtmadan keyingi “Telegramda yozish” tugmasi uchun zaxira
              manzil.
            </p>
          </section>

          <section className="overflow-hidden rounded-2xl bg-[#172641] p-5 text-[#f4efe5]">
            <div className="text-[9px] font-bold uppercase tracking-[.2em] text-[#d6bd92]">
              Ko‘rinishi
            </div>
            <div className="mt-3 font-display text-[22px] leading-tight">
              {form.hero_title_uz || "Sarlavha"}
            </div>
            <p className="mt-2 text-[11px] leading-5 text-white/60">
              {form.hero_text_uz || "Qo‘shimcha matn"}
            </p>
            <Link
              to="/miniapp"
              className="mt-4 inline-flex items-center gap-1.5 text-[10px] font-bold text-[#d6bd92] no-underline hover:underline"
            >
              Mini Appni ochish ↗
            </Link>
          </section>

          <button type="submit" className="wm-btn w-full">
            {t.save}
          </button>
        </aside>
      </div>
    </form>
  );
}

// ---------------- 9. SETTINGS ----------------
export function SettingsPage() {
  const { lang, t } = useLang();
  const { toast } = useToast();
  const [form, setForm] = useState<any>(null);
  const [tab, setTab] = useState<"branding" | "pricing" | "logistics" | "telegram">("branding");

  useEffect(() => {
    adminFetch("/api/admin/settings").then(setForm);
  }, []);

  if (!form) return <SkeletonList count={3} />;

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const updated = await adminFetch("/api/admin/settings", {
        method: "PUT",
        body: JSON.stringify(form),
      });
      setForm(updated);
      toast(t.savedToast);
    } catch (err: any) {
      toast(err.message, "error");
    }
  };

  const samplePrice = calcSellingPrice(
    300,
    0.6,
    Number(form.yuan_rate) || 1750,
    Number(form.shipping_per_kg) || 65000,
    Number(form.margin_pct) || 25,
    null
  );

  return (
    <form onSubmit={save} className="space-y-5">
      <PageHeader
        eyebrow={lang === "ru" ? "Система · White-label" : "Tizim · White-label"}
        title={lang === "ru" ? "Настройки магазина и бренда" : "Do‘kon va Brend sozlamalari"}
        detail={
          lang === "ru"
            ? "Управление брендом магазина, цветами, почтой (BTS / EMU), курсами юаня и карго."
            : "Do‘kon brendi, logotip, ranglar, BTS/EMU pochta tariflari va Xitoy kargo narxlari."
        }
      />

      {/* Sub-tabs */}
      <div className="flex flex-wrap gap-1.5 rounded-2xl border border-border bg-card p-1.5 max-w-xl">
        {[
          { k: "branding", l: lang === "ru" ? "🏷 Бренд магазина" : "🏷 Do‘kon Brendi", s: "White-label" },
          { k: "pricing", l: lang === "ru" ? "💰 Цены и Карго" : "💰 Narx & Kargo", s: "Pricing" },
          { k: "logistics", l: lang === "ru" ? "📮 Почта и Аванс" : "📮 Pochta & Avans", s: "BTS / EMU" },
          { k: "telegram", l: lang === "ru" ? "🔔 Уведомления" : "🔔 Bildirishnomalar", s: "Telegram & Backup" },
        ].map((tb) => (
          <button
            key={tb.k}
            type="button"
            onClick={() => setTab(tb.k as any)}
            className={`flex-1 rounded-xl px-3.5 py-2 text-left transition cursor-pointer border-0 ${
              tab === tb.k
                ? "bg-[#172641] text-[#f5f1e8] shadow-sm"
                : "bg-transparent hover:bg-muted text-foreground"
            }`}
          >
            <div className="text-[11px] font-bold">{tb.l}</div>
            <div
              className={`text-[9px] ${
                tab === tb.k ? "text-white/50" : "text-muted-foreground"
              }`}
            >
              {tb.s}
            </div>
          </button>
        ))}
      </div>

      {/* 1. BRANDING / WHITE-LABEL TAB */}
      {tab === "branding" && (
        <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1fr_340px]">
          <div className="rounded-2xl border border-border bg-card p-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label htmlFor="st-bname" className="wm-label">
                Do‘kon nomi (Brand Name) *
              </label>
              <input
                id="st-bname"
                required
                placeholder="WITHMORE"
                value={form.brand_name || ""}
                onChange={(e) => setForm({ ...form, brand_name: e.target.value })}
                className="wm-input font-bold"
              />
            </div>
            <div>
              <label htmlFor="st-phone" className="wm-label">
                Aloqa telefoni (Mijozlar uchun)
              </label>
              <input
                id="st-phone"
                placeholder="+998 90 123 45 67"
                value={form.contact_phone || ""}
                onChange={(e) => setForm({ ...form, contact_phone: e.target.value })}
                className="wm-input"
              />
            </div>
            <div>
              <label htmlFor="st-slog-uz" className="wm-label">
                Do‘kon shiori (O‘zbekcha)
              </label>
              <input
                id="st-slog-uz"
                placeholder="Klassik erkaklar kiyimi"
                value={form.brand_slogan_uz || ""}
                onChange={(e) => setForm({ ...form, brand_slogan_uz: e.target.value })}
                className="wm-input"
              />
            </div>
            <div>
              <label htmlFor="st-slog-ru" className="wm-label">
                Do‘kon shiori (Ruscha)
              </label>
              <input
                id="st-slog-ru"
                placeholder="Классическая мужская одежда"
                value={form.brand_slogan_ru || ""}
                onChange={(e) => setForm({ ...form, brand_slogan_ru: e.target.value })}
                className="wm-input"
              />
            </div>
            <div>
              <label htmlFor="st-tg-admin" className="wm-label">
                Telegram admin username
              </label>
              <div className="flex items-center rounded-lg border border-border bg-input overflow-hidden">
                <span className="px-2.5 text-xs text-muted-foreground font-bold">@</span>
                <input
                  id="st-tg-admin"
                  placeholder="whitmore_admin"
                  value={(form.contact_username || "").replace(/^@/, "")}
                  onChange={(e) => setForm({ ...form, contact_username: e.target.value.replace(/^@/, "") })}
                  className="flex-1 bg-transparent py-2.5 pr-3 text-xs outline-none"
                />
              </div>
            </div>
            <div>
              <label htmlFor="st-insta" className="wm-label">
                Instagram username
              </label>
              <div className="flex items-center rounded-lg border border-border bg-input overflow-hidden">
                <span className="px-2.5 text-xs text-muted-foreground font-bold">@</span>
                <input
                  id="st-insta"
                  placeholder="whitmore.uz"
                  value={(form.instagram_username || "").replace(/^@/, "")}
                  onChange={(e) => setForm({ ...form, instagram_username: e.target.value.replace(/^@/, "") })}
                  className="flex-1 bg-transparent py-2.5 pr-3 text-xs outline-none"
                />
              </div>
            </div>
            <div>
              <label htmlFor="st-color" className="wm-label">
                Asosiy brend rangi (HEX)
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={form.brand_color || "#172641"}
                  onChange={(e) => setForm({ ...form, brand_color: e.target.value })}
                  className="h-10 w-12 rounded cursor-pointer border border-border bg-transparent p-0.5"
                />
                <input
                  id="st-color"
                  value={form.brand_color || "#172641"}
                  onChange={(e) => setForm({ ...form, brand_color: e.target.value })}
                  className="wm-input font-mono uppercase"
                />
              </div>
            </div>
            <div>
              <label htmlFor="st-accent" className="wm-label">
                Urg‘u rangi / Accent (HEX)
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={form.brand_accent || "#d6bd92"}
                  onChange={(e) => setForm({ ...form, brand_accent: e.target.value })}
                  className="h-10 w-12 rounded cursor-pointer border border-border bg-transparent p-0.5"
                />
                <input
                  id="st-accent"
                  value={form.brand_accent || "#d6bd92"}
                  onChange={(e) => setForm({ ...form, brand_accent: e.target.value })}
                  className="wm-input font-mono uppercase"
                />
              </div>
            </div>

            <div className="sm:col-span-2 pt-3">
              <button type="submit" className="wm-btn">
                💾 {t.save}
              </button>
            </div>
          </div>

          <aside className="rounded-2xl bg-card border border-border p-6 space-y-4">
            <div className="text-[10px] font-bold uppercase tracking-[.2em] text-[#aa8a5e]">
              Do‘kon ko‘rinishi (Jonli namuna)
            </div>
            <div
              className="rounded-xl p-5 text-white shadow-md space-y-3"
              style={{ backgroundColor: form.brand_color || "#172641" }}
            >
              <div className="flex items-center justify-between">
                <span className="font-display text-sm tracking-widest uppercase" style={{ color: form.brand_accent || "#d6bd92" }}>
                  {form.brand_name || "DO'KON NOMI"}
                </span>
                <span className="rounded-full bg-white/20 px-2 py-0.5 text-[9px] font-bold">
                  Mini App
                </span>
              </div>
              <p className="text-xs text-white/80">
                {form.brand_slogan_uz || "Kiyim do'koni shiori"}
              </p>
              <div className="border-t border-white/10 pt-2 text-[10px] text-white/60 flex justify-between">
                <span>@{form.instagram_username || "instagram"}</span>
                <span>@{form.contact_username || "admin"}</span>
              </div>
            </div>
            <p className="text-[11px] text-muted-foreground leading-relaxed">
              Ushbu sozlamalar orqali tizimni boshqa istalgan kiyim do‘koniga 1 daqiqada moslashtirib berishingiz mumkin.
            </p>
          </aside>
        </div>
      )}

      {/* 2. PRICING & CARGO TAB */}
      {tab === "pricing" && (
        <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1fr_340px]">
          <div className="rounded-2xl border border-border bg-card p-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label htmlFor="st-yr" className="wm-label">
                Yuan kursi (so'm)
              </label>
              <input
                id="st-yr"
                type="number"
                value={form.yuan_rate}
                onChange={(e) =>
                  setForm({ ...form, yuan_rate: e.target.value })
                }
                className="wm-input"
              />
            </div>
            <div>
              <label htmlFor="st-mg" className="wm-label">
                Ustama / Margin (%)
              </label>
              <input
                id="st-mg"
                type="number"
                value={form.margin_pct}
                onChange={(e) =>
                  setForm({ ...form, margin_pct: e.target.value })
                }
                className="wm-input"
              />
            </div>
            <div>
              <label htmlFor="st-sh" className="wm-label">
                1 kg yetkazish narxi (so'm)
              </label>
              <input
                id="st-sh"
                type="number"
                value={form.shipping_per_kg}
                onChange={(e) =>
                  setForm({ ...form, shipping_per_kg: e.target.value })
                }
                className="wm-input"
              />
            </div>
            <div>
              <label htmlFor="st-ls" className="wm-label">
                Kam qoldiq chegarasi (dona)
              </label>
              <input
                id="st-ls"
                type="number"
                value={form.low_stock}
                onChange={(e) =>
                  setForm({ ...form, low_stock: e.target.value })
                }
                className="wm-input"
              />
            </div>
            <div className="sm:col-span-2 pt-2">
              <button type="submit" className="wm-btn">
                💾 {t.save}
              </button>
            </div>
          </div>

          <aside className="rounded-2xl bg-[#172641] p-6 text-[#f5f1e8]">
            <div className="text-[10px] font-bold uppercase tracking-[.2em] text-[#d6bd92]">
              Price desk · Hisoblash formulasi
            </div>
            <div className="mt-3 font-mono text-xs leading-relaxed text-white/75">
              (yuan × kurs + vazn × yetkazish) × (1 + ustama%) → 1000 so‘mga
              yaxlitlanadi
            </div>
            <div className="mt-5 border-t border-white/10 pt-4">
              <div className="text-[10px] text-white/55">
                Misol: ¥300 · 0.6 kg
              </div>
              <div className="mt-1 font-display text-[28px] text-[#f3e7d1]">
                {formatPrice(samplePrice)}
              </div>
            </div>
          </aside>
        </div>
      )}

      {/* 3. LOGISTICS & ADVANCE TAB */}
      {tab === "logistics" && (
        <div className="rounded-2xl border border-border bg-card p-6 grid grid-cols-1 gap-4 sm:grid-cols-2 max-w-3xl">
          <div>
            <label htmlFor="st-post-op" className="wm-label">
              Pochta operatorlari (Pochta xizmatlari)
            </label>
            <input
              id="st-post-op"
              placeholder="BTS / EMU / Fargo"
              value={form.post_operators || "BTS / EMU"}
              onChange={(e) => setForm({ ...form, post_operators: e.target.value })}
              className="wm-input font-bold"
            />
          </div>
          <div>
            <label htmlFor="st-post-fee" className="wm-label">
              Pochta narxi (so‘m, 0 = mijoz o‘zi to‘laydi / bepul)
            </label>
            <input
              id="st-post-fee"
              type="number"
              placeholder="0"
              value={form.post_fee || "0"}
              onChange={(e) => setForm({ ...form, post_fee: e.target.value })}
              className="wm-input"
            />
          </div>
          <div>
            <label htmlFor="st-adv" className="wm-label">
              Majburiy oldindan to‘lov (Avans %)
            </label>
            <input
              id="st-adv"
              type="number"
              placeholder="30"
              value={form.advance_pct}
              onChange={(e) => setForm({ ...form, advance_pct: e.target.value })}
              className="wm-input font-bold"
            />
          </div>
          <div>
            <label htmlFor="st-card" className="wm-label">
              To‘lov karta raqami (Avans uchun)
            </label>
            <input
              id="st-card"
              placeholder="8600 1234 5678 9012"
              value={form.payment_card_number || ""}
              onChange={(e) => setForm({ ...form, payment_card_number: e.target.value })}
              className="wm-input font-mono"
            />
          </div>
          <div className="sm:col-span-2">
            <label htmlFor="st-holder" className="wm-label">
              Karta egasi (F.I.Sh yoki Do‘kon nomi)
            </label>
            <input
              id="st-holder"
              placeholder="WITHMORE MENSWEAR"
              value={form.payment_card_holder || ""}
              onChange={(e) => setForm({ ...form, payment_card_holder: e.target.value })}
              className="wm-input uppercase font-bold"
            />
          </div>
          <div className="sm:col-span-2 pt-2">
            <button type="submit" className="wm-btn">
              💾 {t.save}
            </button>
          </div>
        </div>
      )}

      {/* 4. TELEGRAM & BACKUP TAB */}
      {tab === "telegram" && (
        <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
          <div className="rounded-2xl border border-border bg-card p-6 space-y-4">
            <div className="text-sm font-extrabold">
              Telegram bildirishnomalar
            </div>
            {[
              ["notify_admin_order", "Adminga yangi buyurtma xabari"],
              ["notify_admin_lowstock", "Adminga kam qoldiq xabari"],
              ["notify_customer_status", "Mijozga buyurtma holati xabari"],
              ["notify_customer_restock", "Mijozga omborga kelganlik xabari"],
            ].map(([k, label]) => (
              <label
                key={k}
                className="flex items-center justify-between gap-4 border-b border-border/60 py-2.5 last:border-0 text-xs font-semibold"
              >
                <span>{label}</span>
                <input
                  type="checkbox"
                  checked={form[k] === "1"}
                  onChange={(e) =>
                    setForm({ ...form, [k]: e.target.checked ? "1" : "0" })
                  }
                  className="h-4 w-4 accent-[#172641]"
                />
              </label>
            ))}
            <button type="submit" className="wm-btn">
              {t.save}
            </button>
          </div>

          <div className="rounded-2xl border border-border bg-card p-6 space-y-4">
            <div>
              <div className="text-sm font-extrabold">
                💾 Ma'lumotlar bazasini zaxiralash (Backup & Export)
              </div>
              <p className="mt-1 text-xs text-muted-foreground">
                Barcha buyurtmalarni Excel (CSV) formatida yuklab oling yoki
                to'liq ma'lumotlar bazasi (.db) faylini Telegram bot orqali
                o'zingizga yuboring.
              </p>
            </div>
            <div className="flex flex-wrap gap-2.5 pt-2">
              <a
                href="/api/admin/backup/orders.csv"
                target="_blank"
                rel="noreferrer"
                className="wm-btn-outline text-xs no-underline inline-flex items-center gap-1.5"
              >
                📥 Buyurtmalarni yuklab olish (CSV / Excel)
              </a>
              <button
                type="button"
                onClick={async () => {
                  try {
                    await adminFetch("/api/admin/backup/telegram", {
                      method: "POST",
                    });
                    toast("Zaxira nusxasi Telegramga yuborildi!");
                  } catch (err: any) {
                    toast(err.message, "error");
                  }
                }}
                className="wm-btn text-xs"
              >
                ✈️ Telegramga zaxira yuborish (.db + .csv)
              </button>
            </div>
          </div>
        </div>
      )}
    </form>
  );
}

// ---------------- 10. MARKETING ----------------
export function MarketingPage() {
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
    ? ((totals.orders / totals.visits) * 100).toFixed(1)
    : "0.0";

  const cleanSlug = (s: string) =>
    s
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9._]+/g, "_")
      .replace(/^_+|_+$/g, "");

  const builtWebLink =
    utmSource.trim() && utmCampaign.trim()
      ? `${window.location.origin}/miniapp?utm_source=${encodeURIComponent(
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
    <div className="space-y-6">
      <PageHeader
        eyebrow="Marketing · Manbalar"
        title="Reklama manbalari"
        detail="Mini Appga kim qaysi havola orqali kelgani va buyurtma bergani."
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

      <div>
        <label htmlFor="mk-q" className="wm-label">
          {t.search}
        </label>
        <input
          id="mk-q"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="wm-input max-w-sm"
        />
      </div>

      {loading ? (
        <SkeletonList count={3} />
      ) : filtered.length === 0 ? (
        <EmptyState text="Ma'lumot topilmadi" />
      ) : (
        <div className="overflow-hidden rounded-2xl border border-border bg-card">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[680px] text-left text-xs">
              <thead className="bg-[#f6f2e9] text-[9px] font-bold uppercase tracking-[.12em] text-muted-foreground">
                <tr>
                  <th className="px-5 py-3">Manba (Source)</th>
                  <th className="px-4 py-3">Kanal (Medium)</th>
                  <th className="px-4 py-3">Kampaniya</th>
                  <th className="px-4 py-3 text-right">Tashriflar</th>
                  <th className="px-4 py-3 text-right">Buyurtmalar</th>
                  <th className="px-5 py-3 text-right">Summa</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((r, i) => (
                  <tr key={i} className="border-t border-border/70">
                    <td className="px-5 py-3 font-bold">{r.source}</td>
                    <td className="px-4 py-3 text-muted-foreground">
                      {r.medium || "-"}
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">
                      {r.campaign || "-"}
                    </td>
                    <td className="px-4 py-3 text-right">{r.visits}</td>
                    <td className="px-4 py-3 text-right font-semibold">
                      {r.orders}
                    </td>
                    <td className="px-5 py-3 text-right font-extrabold">
                      {formatPrice(r.amount)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Instagram Quick-Ready Funnel Links */}
      <section className="rounded-2xl border border-[#d9ccb3] bg-[#faf5ea] p-6 space-y-4">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <div>
            <div className="text-[10px] font-bold uppercase tracking-[.16em] text-[#8d6e43]">
              📸 Instagram Voronka (@{botUsername})
            </div>
            <h2 className="mt-1 text-[15px] font-extrabold text-[#172641]">
              Instagram uchun tayyor havolalar (Bio, Stories, Reels, Target)
            </h2>
            <p className="mt-0.5 text-xs text-muted-foreground">
              Mijoz Instagramdan bosganda to‘g‘ri @{botUsername} botiga va Mini
              Appga kiradi, statistikasi esa yuqoridagi jadvalga avtomatik
              yoziladi.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          {[
            {
              title: "📌 Instagram Bio (Profil bosh sahifasi)",
              desc: "Profil tavsifiga (Website qatoriga) qo‘yish uchun",
              link: `https://t.me/${botUsername}?start=instagram-bio-profil`,
            },
            {
              title: "📲 Instagram Stories («Havola / Ссылка» stikeri)",
              desc: "Kunlik obzor va yangi modellar storiysi uchun",
              link: `https://t.me/${botUsername}?start=instagram-story-kunlik`,
            },
            {
              title: "🎬 Instagram Reels & Postlar (Direct / ManyChat)",
              desc: "«Kommentga + yozing» avto-javobi yoki Reels uchun",
              link: `https://t.me/${botUsername}?start=instagram-reels-video`,
            },
            {
              title: "🎯 Instagram Target Reklama (Ads Manager)",
              desc: "Target reklamadan kelgan xaridorlarni aniq hisoblash uchun",
              link: `https://t.me/${botUsername}?start=instagram-target-ads`,
            },
          ].map((item) => (
            <div
              key={item.link}
              className="flex flex-col justify-between gap-2 rounded-xl border border-border bg-card p-3.5"
            >
              <div>
                <div className="text-xs font-extrabold text-[#172641]">
                  {item.title}
                </div>
                <div className="text-[11px] text-muted-foreground">
                  {item.desc}
                </div>
              </div>
              <div className="flex items-center justify-between gap-2 rounded-lg bg-[#faf8f3] px-2.5 py-1.5 font-mono text-[11px]">
                <span className="truncate">{item.link}</span>
                <button
                  type="button"
                  onClick={() => copyText(item.link, item.title)}
                  className="wm-btn shrink-0 text-[11px] py-1 px-2.5 min-h-[28px]"
                >
                  Nusxalash
                </button>
              </div>
            </div>
          ))}
        </div>
        <div className="rounded-xl border border-[#e3d7c1] bg-card/80 px-4 py-2.5 text-[11px] text-muted-foreground">
          💡 <b>Alohida mahsulotni Instagramda reklama qilish:</b>{" "}
          <Link to="/admin/products" className="font-bold text-[#172641] underline">
            Mahsulotlar
          </Link>{" "}
          bo‘limida har bir kiyim kartochkasida <b>«📸 Insta link»</b> tugmasi
          bor — mijoz uni bossa, bot o‘sha mahsulot rasmi, narxi va o‘lchamini
          darhol chiqarib beradi!
        </div>
      </section>

      {/* Replit UTM Link Builder Card */}
      <section className="rounded-2xl border border-border bg-card p-6 space-y-4">
        <h2 className="text-[14px] font-extrabold">
          Maxsus reklama havolasi yaratish (Konstruktor)
        </h2>
        <p className="text-xs text-muted-foreground">
          Har bir bloger, kanal yoki reklama kampaniyasi uchun alohida havola
          yarating — yuqoridagi jadvalda shu nomlar bilan ko‘rinadi.
        </p>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
          <div>
            <label htmlFor="utm-src" className="wm-label">
              Manba (Source) *
            </label>
            <input
              id="utm-src"
              value={utmSource}
              onChange={(e) => setUtmSource(e.target.value)}
              placeholder="instagram, telegram_kanal..."
              className="wm-input"
            />
          </div>
          <div>
            <label htmlFor="utm-med" className="wm-label">
              Kanal (Medium)
            </label>
            <input
              id="utm-med"
              value={utmMedium}
              onChange={(e) => setUtmMedium(e.target.value)}
              placeholder="reels, story, bio, bloger..."
              className="wm-input"
            />
          </div>
          <div>
            <label htmlFor="utm-cmp" className="wm-label">
              Kampaniya *
            </label>
            <input
              id="utm-cmp"
              value={utmCampaign}
              onChange={(e) => setUtmCampaign(e.target.value)}
              placeholder="kuz_kostyumlar"
              className="wm-input"
            />
          </div>
        </div>
        {builtBotLink && (
          <div className="space-y-2.5">
            <div className="rounded-xl border border-border bg-[#faf8f3] p-3">
              <div className="mb-1 text-[10px] font-bold uppercase tracking-wider text-[#172641]">
                1. Telegram Bot + Mini App havolasi (Tavsiya etiladi — mijoz botda qoladi):
              </div>
              <div className="flex flex-wrap items-center gap-2 font-mono text-xs">
                <span className="break-all flex-1">{builtBotLink}</span>
                <button
                  type="button"
                  onClick={() => copyText(builtBotLink, "Telegram Bot havolasi")}
                  className="wm-btn text-xs py-1.5 px-3 min-h-[34px]"
                >
                  Nusxalash
                </button>
              </div>
            </div>

            <div className="rounded-xl border border-border bg-[#faf8f3] p-3">
              <div className="mb-1 text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                2. To‘g‘ridan-to‘g‘ri Veb-katalog havolasi (Telegramsiz brauzerda ochish):
              </div>
              <div className="flex flex-wrap items-center gap-2 font-mono text-xs">
                <span className="break-all flex-1">{builtWebLink}</span>
                <button
                  type="button"
                  onClick={() => copyText(builtWebLink, "Veb havola")}
                  className="wm-btn-ghost text-xs py-1.5 px-3 min-h-[34px]"
                >
                  Nusxalash
                </button>
              </div>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

// ---------------- GROWTH / O'SISH ----------------
export function GrowthPage() {
  const { toast } = useToast();
  const [settings, setSettings] = useState<any>(null);

  useEffect(() => {
    adminFetch("/api/admin/settings")
      .then(setSettings)
      .catch((e) => toast(e.message, "error"));
  }, []);

  if (!settings) return <SkeletonList count={4} />;

  const toggleKey = async (k: string) => {
    const next = { ...settings, [k]: settings[k] === "1" ? "0" : "1" };
    setSettings(next);
    await adminFetch("/api/admin/settings", {
      method: "PUT",
      body: JSON.stringify(next),
    });
    toast("Saqlandi");
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <PageHeader
        eyebrow="Growth · O‘sish"
        title="Mijoz xabarlari va o‘sish"
        detail="Telegram xabarnomalari, qayta kelganda xabar berish va konversiya vositalari."
      />

      <section className="rounded-2xl border border-border bg-card p-6 space-y-4">
        <h2 className="text-[14px] font-extrabold">Bot xabarnomalari</h2>
        <p className="text-xs text-muted-foreground">
          Yoqilgandan keyin yangi buyurtma holati o‘zgarishlari va zaxiraga
          qaytgan mahsulotlar haqida mijozlarga avtomatik Telegram xabarlari
          yuboriladi.
        </p>
        <div className="divide-y divide-border/70">
          {[
            [
              "notify_customer_status",
              "Buyurtma holati xabarlari",
              "Admin buyurtma holatini o‘zgartirganda mijozga Telegram orqali xabar.",
            ],
            [
              "notify_customer_restock",
              "Qayta kelganda xabar",
              "Mini Appda mijozlarga tugagan variantga obuna bo‘lish imkonini beradi va zaxira to‘ldirilganda xabar yuboradi.",
            ],
            [
              "notify_admin_order",
              "Adminga yangi buyurtma xabari",
              "Yangi buyurtma tushganda biriktirilgan adminga darhol Telegram xabar.",
            ],
            [
              "notify_admin_lowstock",
              "Adminga kam qoldiq ogohlantirishi",
              "Zaxira belgilangan chegaradan kamayganda ogohlantirish.",
            ],
          ].map(([k, title, desc]) => (
            <div
              key={k}
              className="flex items-center justify-between gap-4 py-3.5"
            >
              <div>
                <div className="text-xs font-bold">{title}</div>
                <div className="text-[11px] text-muted-foreground">{desc}</div>
              </div>
              <input
                type="checkbox"
                checked={settings[k] === "1"}
                onChange={() => toggleKey(k)}
                className="h-4 w-4 accent-[#172641]"
              />
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

// ---------------- 11. ACTIVITY LOG (OWNER ONLY) ----------------
export function AuditPage() {
  const { t } = useLang();
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");

  useEffect(() => {
    setLoading(true);
    adminFetch(`/api/admin/audit?q=${encodeURIComponent(q)}`)
      .then((res) => setItems(res.items || []))
      .finally(() => setLoading(false));
  }, [q]);

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Audit · Faoliyat"
        title="Jamoa faoliyati"
        detail="Kim, qachon va nima o‘zgartirgani."
      />

      <div>
        <label htmlFor="au-q" className="wm-label">
          {t.search}
        </label>
        <input
          id="au-q"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Admin yoki amal bo‘yicha qidirish…"
          className="wm-input max-w-sm"
        />
      </div>

      {loading ? (
        <SkeletonList count={4} />
      ) : items.length === 0 ? (
        <EmptyState text="Yozuvlar topilmadi" />
      ) : (
        <ol className="divide-y divide-border/60 overflow-hidden rounded-2xl border border-border bg-card list-none m-0 p-0">
          {items.map((a) => (
            <li key={a.id} className="flex items-start gap-4 px-5 py-3.5">
              <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#f1eadc] font-display text-xs text-[#806a48]">
                {(a.admin || "A").slice(0, 1).toUpperCase()}
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-xs">
                  <strong>{a.admin}</strong> · {a.action} ({a.entity} #
                  {a.entity_id}) {a.detail ? `— ${a.detail}` : ""}
                </div>
                <div className="mt-0.5 text-[10px] text-muted-foreground">
                  {a.at}
                </div>
              </div>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
