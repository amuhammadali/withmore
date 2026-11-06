import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { adminFetch } from "../api";
import { formatPrice, useLang } from "../i18n";
import { EmptyState, SkeletonList, StatusBadge, useToast } from "../ui";
import { PageHeader } from "./AdminPages";

// ---------------- 1. POSTAL DISPATCH & MANIFEST (BTS / EMU JO'NATISH REESTRI) ----------------
export function ChinaProcurementPage() {
  const { t } = useLang();
  const { toast } = useToast();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("all_ready");
  const [trackingEdits, setTrackingEdits] = useState<Record<number, string>>({});
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [bulkUpdating, setBulkUpdating] = useState(false);

  const load = () => {
    setLoading(true);
    adminFetch(`/api/admin/ops/dispatch-list?status=${status}`)
      .then((res) => {
        setData(res);
        setSelectedIds([]);
      })
      .catch((e) => toast(e.message, "error"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, [status]);

  const copyManifest = () => {
    if (!data || !data.orders || data.orders.length === 0) {
      toast("Reestrda buyurtmalar yo'q", "error");
      return;
    }
    const lines = [
      `📦 BTS / EMU POCHTA REESTRI (${new Date().toLocaleDateString("uz-UZ")}):`,
      `Jami buyurtmalar: ${data.orders.length} ta | Jami kiyimlar: ${data.total_qty} dona`,
      "--------------------------------------------------",
    ];
    data.orders.forEach((ord: any, idx: number) => {
      const payStatus =
        ord.remaining > 0
          ? `⚠️ QOLDIQ (UNDIRILSIN): ${formatPrice(ord.remaining)}`
          : "✅ TO'LIQ TO'LANGAN";
      lines.push(
        `${idx + 1}. [${ord.code}] ${ord.customer_name} | Tel: ${ord.phone}`
      );
      lines.push(`   📍 Manzil/Filial: ${ord.city}, ${ord.address || ""}`);
      lines.push(`   👔 Mahsulotlar: ${ord.items_summary}`);
      lines.push(`   💵 To'lov: ${payStatus}`);
      if (ord.tracking) {
        lines.push(`   📦 Trek-kod: ${ord.tracking}`);
      }
      lines.push("");
    });
    navigator.clipboard.writeText(lines.join("\n"));
    toast("Pochta reestri nusxalandi! Kuryerga yuborishingiz mumkin.", "success");
  };

  const handleBulkStatus = async (newStatus: string) => {
    const ids = selectedIds.length > 0 ? selectedIds : data?.order_ids || [];
    if (ids.length === 0) {
      toast("Buyurtmalar tanlanmagan", "error");
      return;
    }
    setBulkUpdating(true);
    try {
      const res = await adminFetch("/api/admin/ops/bulk-status", {
        method: "POST",
        body: JSON.stringify({
          order_ids: ids,
          status: newStatus,
        }),
      });
      toast(`${res.updated} ta buyurtma holati "${res.status_uz}"ga o'zgartirildi!`, "success");
      load();
    } catch (e: any) {
      toast(e.message, "error");
    } finally {
      setBulkUpdating(false);
    }
  };

  const toggleSelectAll = () => {
    if (!data?.orders) return;
    if (selectedIds.length === data.orders.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(data.orders.map((o: any) => o.id));
    }
  };

  const toggleSelect = (id: number) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const printList = () => {
    window.print();
  };

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Logistika · Domestic Delivery"
        title="📦 Pochta & Jo'natish Reestri (BTS / EMU)"
        detail="Mijozlar buyurtmalarini saralash, qadoqlash, BTS yoki EMU pochta kuryerlariga topshirish reestri va rasmiy nakladnoylar."
        action={
          <div className="flex flex-wrap items-center gap-2">
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="wm-input text-xs w-auto min-w-[200px]"
            >
              <option value="all_ready">Barcha tayyor buyurtmalar</option>
              <option value="paid">Tasdiqlangan (paid)</option>
              <option value="preparing">Qadoqlanmoqda (preparing)</option>
              <option value="ready_to_ship">Jo'natishga tayyor (ready_to_ship)</option>
              <option value="in_transit">Pochtada yo'lda (in_transit)</option>
              <option value="new">Yangi buyurtmalar</option>
            </select>
            <button
              type="button"
              onClick={copyManifest}
              className="wm-btn-outline text-xs py-2 px-3 flex items-center gap-1.5"
            >
              📋 Reestrni nusxalash
            </button>
            <button
              type="button"
              onClick={printList}
              className="wm-btn text-xs py-2 px-3"
            >
              🖨 Chop etish / PDF
            </button>
          </div>
        }
      />

      {loading ? (
        <SkeletonList count={4} />
      ) : !data || data.orders.length === 0 ? (
        <EmptyState text="Ushbu holatda jo'natishga tayyor buyurtmalar topilmadi." />
      ) : (
        <>
          {/* Summary Stat Cards */}
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <div className="rounded-2xl border border-border bg-card p-4">
              <div className="text-[9px] font-bold uppercase tracking-[.14em] text-muted-foreground">
                Buyurtmalar soni
              </div>
              <div className="mt-1 font-display text-[26px] font-medium text-[#172641]">
                {data.orders_count} ta
              </div>
              <div className="mt-0.5 text-[11px] text-muted-foreground">
                Jo'natishga tayyor posilkalar
              </div>
            </div>

            <div className="rounded-2xl border border-border bg-card p-4">
              <div className="text-[9px] font-bold uppercase tracking-[.14em] text-[#8a6c43]">
                Jami kiyimlar soni
              </div>
              <div className="mt-1 font-display text-[26px] font-medium text-[#8a6c43]">
                {data.total_qty} dona
              </div>
              <div className="mt-0.5 text-[11px] text-muted-foreground">
                Ombordan saralangan
              </div>
            </div>

            <div className="rounded-2xl border border-border bg-card p-4">
              <div className="text-[9px] font-bold uppercase tracking-[.14em] text-[#397252]">
                Umumiy buyurtma summasi
              </div>
              <div className="mt-1 font-display text-[26px] font-medium text-[#397252]">
                {formatPrice(data.total_uzs)}
              </div>
              <div className="mt-0.5 text-[11px] text-muted-foreground">
                Katalog qiymati
              </div>
            </div>

            <div className="rounded-2xl border border-border bg-card p-4">
              <div className="text-[9px] font-bold uppercase tracking-[.14em] text-muted-foreground">
                Modellar xili
              </div>
              <div className="mt-1 font-display text-[26px] font-medium text-[#172641]">
                {data.items.length} xil
              </div>
              <div className="mt-0.5 text-[11px] text-muted-foreground">
                O‘lcham va ranglar kesimida
              </div>
            </div>
          </div>

          {/* Bulk Action Strip */}
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-[#172641]/15 bg-[#faf8f3] p-3 text-xs">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={selectedIds.length === data.orders.length && data.orders.length > 0}
                onChange={toggleSelectAll}
                className="h-4 w-4 rounded border-slate-300 text-[#172641] cursor-pointer"
              />
              <span className="font-bold text-[#172641]">
                {selectedIds.length > 0
                  ? `${selectedIds.length} ta buyurtma tanlandi`
                  : `Barchasini tanlash (${data.orders.length} ta)`}
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                disabled={bulkUpdating}
                onClick={() => handleBulkStatus("in_transit")}
                className="rounded-xl bg-[#172641] px-3.5 py-1.5 text-xs font-bold text-white hover:bg-[#25395b] transition cursor-pointer border-0 shadow-sm"
              >
                🚚 "Pochtada yo'lda (BTS / EMU)" ga o'tkazish
              </button>
              <button
                type="button"
                disabled={bulkUpdating}
                onClick={() => handleBulkStatus("delivered")}
                className="rounded-xl bg-[#2c6e49] px-3.5 py-1.5 text-xs font-bold text-white hover:bg-[#22573a] transition cursor-pointer border-0 shadow-sm"
              >
                🎉 "Yetkazildi" qilish
              </button>
            </div>
          </div>

          {/* Aggregated Warehouse Packing List */}
          <div className="overflow-hidden rounded-2xl border border-border bg-card">
            <div className="border-b border-border bg-[#faf8f3] px-5 py-3 flex items-center justify-between">
              <span className="text-xs font-bold text-[#172641]">
                Ombordan yig'ish varaqasi (Qaysi modeldan nechta qadoqlash kerak)
              </span>
              <span className="text-[11px] text-muted-foreground">
                Holati: <StatusBadge status={data.status} />
              </span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[700px] text-left text-xs">
                <thead className="bg-[#f6f2e9] text-[9px] font-bold uppercase tracking-[.12em] text-muted-foreground">
                  <tr>
                    <th className="px-5 py-2.5">Rasm / Model</th>
                    <th className="px-4 py-2.5">O‘lcham</th>
                    <th className="px-4 py-2.5">Rang</th>
                    <th className="px-4 py-2.5 text-center">Soni</th>
                    <th className="px-4 py-2.5">Tegishli buyurtmalar</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/70">
                  {data.items.map((it: any, idx: number) => (
                    <tr key={idx} className="hover:bg-[#faf8f3]/60 transition">
                      <td className="px-5 py-2.5">
                        <div className="flex items-center gap-3">
                          {it.thumb ? (
                            <img
                              src={`/uploads/${it.thumb}`}
                              alt={it.name}
                              className="h-10 w-9 rounded-lg object-cover border border-border"
                            />
                          ) : (
                            <div className="flex h-10 w-9 items-center justify-center rounded-lg bg-[#eee8db] font-display text-sm text-[#8a6c43]">
                              W
                            </div>
                          )}
                          <div>
                            <div className="font-extrabold text-[12px] text-[#172641]">
                              {it.name}
                            </div>
                            {it.sku && (
                              <div className="text-[10px] text-muted-foreground">
                                Artikul: {it.sku}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-2.5">
                        <span className="rounded-md bg-muted px-2 py-0.5 text-xs font-bold text-[#172641]">
                          {it.size}
                        </span>
                      </td>
                      <td className="px-4 py-2.5 text-muted-foreground font-semibold">
                        {it.color || "—"}
                      </td>
                      <td className="px-4 py-2.5 text-center">
                        <span className="inline-flex h-6 min-w-[24px] items-center justify-center rounded-full bg-[#172641] px-2 text-xs font-extrabold text-[#f4efe5]">
                          {it.qty} dona
                        </span>
                      </td>
                      <td className="px-4 py-2.5">
                        <div className="flex flex-wrap gap-1 max-w-[220px]">
                          {it.orders.map((code: string) => (
                            <Link
                              key={code}
                              to={`/admin/orders`}
                              className="font-mono text-[10px] font-bold text-[#172641] bg-[#ece5d8] px-1.5 py-0.5 rounded no-underline hover:underline"
                            >
                              {code}
                            </Link>
                          ))}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Full BTS / EMU Dispatch Manifest Table */}
          <div className="overflow-hidden rounded-2xl border border-border bg-card">
            <div className="border-b border-border bg-[#faf8f3] px-5 py-3 flex items-center justify-between">
              <span className="text-xs font-bold text-[#172641]">
                📮 BTS / EMU Pochta Reestri (Posilka qabul qiluvchilar ro'yxati)
              </span>
              <span className="text-[11px] text-muted-foreground font-semibold">
                Jami: {data.orders.length} ta posilka
              </span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[900px] text-left text-xs">
                <thead className="bg-[#f6f2e9] text-[9px] font-bold uppercase tracking-[.12em] text-muted-foreground">
                  <tr>
                    <th className="px-3 py-3 w-8">#</th>
                    <th className="px-4 py-3">Buyurtma</th>
                    <th className="px-4 py-3">Qabul qiluvchi & Tel</th>
                    <th className="px-4 py-3">Shahar / Manzil / Filial</th>
                    <th className="px-4 py-3">Kiyimlar</th>
                    <th className="px-4 py-3 text-right">To'lov / Qoldiq</th>
                    <th className="px-4 py-3">Trek-kod</th>
                    <th className="px-4 py-3 text-center">Hujjat</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/70">
                  {data.orders.map((ord: any) => {
                    const isSelected = selectedIds.includes(ord.id);
                    return (
                      <tr
                        key={ord.id}
                        className={`transition ${
                          isSelected ? "bg-amber-50/50" : "hover:bg-[#faf8f3]/60"
                        }`}
                      >
                        <td className="px-3 py-3">
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={() => toggleSelect(ord.id)}
                            className="h-4 w-4 rounded border-slate-300 text-[#172641] cursor-pointer"
                          />
                        </td>
                        <td className="px-4 py-3 font-mono font-bold text-[#172641]">
                          <Link
                            to={`/admin/orders`}
                            className="text-[#172641] hover:underline"
                          >
                            {ord.code}
                          </Link>
                          <div className="text-[10px] text-muted-foreground font-normal">
                            {ord.date}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="font-bold text-slate-900">
                            {ord.customer_name}
                          </div>
                          {ord.phone && (
                            <a
                              href={`tel:${ord.phone}`}
                              className="text-[11px] text-[#8a6c43] font-semibold hover:underline"
                            >
                              📞 {ord.phone}
                            </a>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <div className="font-bold text-slate-900">
                            {ord.city}
                          </div>
                          <div className="text-[11px] text-muted-foreground line-clamp-1">
                            {ord.address || "Pochta filiali"}
                          </div>
                        </td>
                        <td className="px-4 py-3 text-[11px] text-slate-800">
                          {ord.items_summary}
                        </td>
                        <td className="px-4 py-3 text-right font-mono">
                          {ord.remaining > 0 ? (
                            <div>
                              <div className="font-bold text-[#a3463c]">
                                {formatPrice(ord.remaining)}
                              </div>
                              <div className="text-[9px] text-[#a3463c] uppercase font-bold">
                                Qoldiq (Undirish)
                              </div>
                            </div>
                          ) : (
                            <span className="inline-block rounded-md bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-800">
                              ✓ To'liq to'langan
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3 font-mono text-[11px]">
                          {ord.tracking ? (
                            <span className="rounded bg-slate-100 px-2 py-0.5 font-bold text-slate-900">
                              {ord.tracking}
                            </span>
                          ) : (
                            <span className="text-muted-foreground text-[10px]">
                              Kiritilmagan
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-center">
                          <a
                            href={`/api/admin/ops/label/${ord.id}`}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-1 rounded-lg border border-slate-300 bg-white px-2.5 py-1 text-xs font-bold text-slate-800 hover:bg-slate-50 no-underline shadow-2xs"
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
        </>
      )}
    </div>
  );
}

// ---------------- 2. FINANCE & NET PROFIT (SOF FOYDA KALKULYATORI) ----------------
export function FinanceProfitPage() {
  const { toast } = useToast();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  useEffect(() => {
    setLoading(true);
    adminFetch(`/api/admin/ops/finance?days=${days}`)
      .then(setData)
      .catch((e) => toast(e.message, "error"))
      .finally(() => setLoading(false));
  }, [days]);

  if (loading || !data) return <SkeletonList count={5} />;

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Moliya · Profit Analytics"
        title="💰 Sof Foyda va Moliya Tahlili"
        detail={`Oxirgi ${days} kundagi tovar tannarxi va BTS/EMU pochta xarajatlari chegirilgan sof foyda tahlili.`}
        action={
          <div className="flex items-center gap-2">
            <div className="flex rounded-xl border border-border bg-card p-1">
              {[7, 30, 90, 365].map((d) => (
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
                  {d === 365 ? "1 yil" : `${d} kun`}
                </button>
              ))}
            </div>
          </div>
        }
      />

      {/* 4 Cards for Financial Breakdown */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Gross Revenue */}
        <div className="rounded-2xl border border-border bg-card p-5">
          <div className="text-[9px] font-bold uppercase tracking-[.14em] text-muted-foreground">
            Jami Sotuv (Tushum)
          </div>
          <div className="mt-1 font-display text-[26px] font-medium text-[#172641]">
            {formatPrice(data.revenue)}
          </div>
          <div className="mt-1 text-[11px] text-muted-foreground">
            {data.orders} ta tasdiqlangan buyurtma
          </div>
        </div>

        {/* Goods Cost */}
        <div className="rounded-2xl border border-border bg-card p-5">
          <div className="text-[9px] font-bold uppercase tracking-[.14em] text-[#8a6c43]">
            Mahsulot Tannarxi (COGS)
          </div>
          <div className="mt-1 font-display text-[26px] font-medium text-[#8a6c43]">
            {formatPrice(data.cost_goods)}
          </div>
          <div className="mt-1 text-[11px] text-muted-foreground">
            Kiyimlar ishlab chiqarish / xarid narxi
          </div>
        </div>

        {/* Post Shipping */}
        <div className="rounded-2xl border border-border bg-card p-5">
          <div className="text-[9px] font-bold uppercase tracking-[.14em] text-[#397252]">
            Pochta Xarajati (BTS / EMU)
          </div>
          <div className="mt-1 font-display text-[26px] font-medium text-[#397252]">
            {formatPrice(data.post_total)}
          </div>
          <div className="mt-1 text-[11px] text-muted-foreground">
            Viloyatlarga yetkazib berish to'lovi
          </div>
        </div>

        {/* Net Profit */}
        <div className="rounded-2xl border border-[#d6bd92] bg-[#172641] p-5 text-[#f4efe5]">
          <div className="text-[9px] font-bold uppercase tracking-[.14em] text-[#d6bd92]">
            Sof Foyda (Net Profit)
          </div>
          <div className="mt-1 font-display text-[28px] font-medium text-[#f4efe5]">
            {formatPrice(data.profit)}
          </div>
          <div className="mt-1 text-[11px] text-[#d6bd92]">
            Rentabellik: <b>{data.margin_pct}%</b>
          </div>
        </div>
      </div>

      {/* Additional Financial Metrics */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded-2xl border border-border bg-card p-5">
          <div className="text-xs font-bold text-[#172641]">
            💳 Mijozlardan olingan to‘lov
          </div>
          <div className="mt-2 text-xl font-display font-medium text-[#2b6cb0]">
            {formatPrice(data.paid)}
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground">
            Avans va to‘liq to‘langan summalar
          </p>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5">
          <div className="text-xs font-bold text-[#172641]">
            ⏳ Qoldiq to‘lov (Pochtada undiriladigan)
          </div>
          <div className="mt-2 text-xl font-display font-medium text-[#a8742a]">
            {formatPrice(data.debt)}
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground">
            Mijoz posilkani BTS/EMU'dan olayotganda to'laydigan qoldiq
          </p>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5">
          <div className="text-xs font-bold text-[#172641]">
            🏷 Berilgan chegirmalar
          </div>
          <div className="mt-2 text-xl font-display font-medium text-muted-foreground">
            {formatPrice(data.discounts)}
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground">
            Promokodlar va aksiyalar bo‘yicha chegirma
          </p>
        </div>
      </div>

      {/* Order-by-Order Real Net Profit */}
      <div className="overflow-hidden rounded-2xl border border-border bg-card">
        <div className="border-b border-border bg-[#faf8f3] px-5 py-3 flex items-center justify-between">
          <div>
            <h2 className="text-[13px] font-extrabold text-[#172641]">
              🧾 Har bir buyurtma bo‘yicha sof foyda tahlili (Unit Economics)
            </h2>
            <div className="text-[11px] text-muted-foreground mt-0.5">
              Har bir kiyim buyurtmasining tushumi, tannarxi, pochta xarajati va sof foydasi.
            </div>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#f6f2e9] text-[9px] font-bold uppercase tracking-[.12em] text-muted-foreground">
              <tr>
                <th className="px-5 py-3">Buyurtma & Mijoz</th>
                <th className="px-4 py-3">Mahsulotlar</th>
                <th className="px-4 py-3 text-right">Sotuv Narxi</th>
                <th className="px-4 py-3 text-right">Tannarx (COGS)</th>
                <th className="px-4 py-3 text-right">Pochta (BTS/EMU)</th>
                <th className="px-5 py-3 text-right">Sof Foyda</th>
                <th className="px-4 py-3 text-center">Marja</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/70">
              {(data.order_details || []).map((ord: any) => {
                const isPositive = ord.profit > 0;
                return (
                  <tr key={ord.id} className="hover:bg-[#faf8f3]/60 transition">
                    <td className="px-5 py-3">
                      <div className="font-bold text-[#172641] font-mono">
                        {ord.code}
                      </div>
                      <div className="text-[11px] text-muted-foreground">
                        {ord.customer_name} · {ord.date}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-800 text-[11px] max-w-[240px]">
                      {ord.items_summary}
                    </td>
                    <td className="px-4 py-3 text-right font-mono font-bold text-[#172641]">
                      {formatPrice(ord.revenue)}
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-muted-foreground">
                      {formatPrice(ord.cogs)}
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-muted-foreground">
                      {formatPrice(ord.delivery)}
                    </td>
                    <td
                      className={`px-5 py-3 text-right font-mono font-extrabold ${
                        isPositive ? "text-[#2c6e49]" : "text-[#a3463c]"
                      }`}
                    >
                      {formatPrice(ord.profit)}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className={`inline-block rounded-md px-2 py-0.5 text-[10px] font-bold ${
                          isPositive
                            ? "bg-[#2c6e49]/10 text-[#2c6e49]"
                            : "bg-[#a3463c]/10 text-[#a3463c]"
                        }`}
                      >
                        {ord.margin_pct}%
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
