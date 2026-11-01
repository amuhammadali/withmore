import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { adminFetch } from "../api";
import { formatPrice, useLang } from "../i18n";
import { EmptyState, SkeletonList, StatusBadge, useToast } from "../ui";
import { PageHeader } from "./AdminPages";

// ---------------- 1. CHINA PROCUREMENT (XITOY ZAKUP VARAQASI) ----------------
export function ChinaProcurementPage() {
  const { t } = useLang();
  const { toast } = useToast();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("paid");
  const [supplierEdits, setSupplierEdits] = useState<Record<number, string>>({});
  const [savingPid, setSavingPid] = useState<number | null>(null);

  const load = () => {
    setLoading(true);
    adminFetch(`/api/admin/ops/china-list?status=${status}`)
      .then(setData)
      .catch((e) => toast(e.message, "error"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, [status]);

  const saveSupplierUrl = async (pid: number) => {
    const url = supplierEdits[pid];
    if (url === undefined) return;
    setSavingPid(pid);
    try {
      await adminFetch(`/api/admin/ops/supplier/${pid}`, {
        method: "PUT",
        body: JSON.stringify({ url }),
      });
      toast("Xitoy havolasi saqlandi!");
      load();
    } catch (e: any) {
      toast(e.message, "error");
    } finally {
      setSavingPid(null);
    }
  };

  const printList = () => {
    window.print();
  };

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Xaridlar · Procurement"
        title="🇨🇳 Xitoy Zakup Varaqasi"
        detail="To‘lovi tasdiqlangan buyurtmalarni 1688, Taobao va Poizon'dan bir vaqtda xarid qilish ro‘yxati."
        action={
          <div className="flex flex-wrap items-center gap-2">
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="wm-input text-xs w-auto min-w-[170px]"
            >
              <option value="paid">To‘langan (Avans olingan)</option>
              <option value="new">Yangi buyurtmalar</option>
              <option value="awaiting_payment">To‘lov kutilmoqda</option>
              <option value="ordered_china">Xitoyda sotib olingan</option>
            </select>
            <button
              type="button"
              onClick={printList}
              className="wm-btn text-xs py-2 px-3.5"
            >
              🖨 Chop etish / PDF
            </button>
          </div>
        }
      />

      {loading ? (
        <SkeletonList count={4} />
      ) : !data || data.items.length === 0 ? (
        <EmptyState text="Ushbu holatda xarid qilinadigan tovarlar topilmadi." />
      ) : (
        <>
          {/* Summary Stat Cards */}
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <div className="rounded-2xl border border-border bg-card p-4">
              <div className="text-[9px] font-bold uppercase tracking-[.14em] text-muted-foreground">
                Jami buyumlar soni
              </div>
              <div className="mt-1 font-display text-[26px] font-medium text-[#172641]">
                {data.total_qty} dona
              </div>
              <div className="mt-0.5 text-[11px] text-muted-foreground">
                {data.orders_count} ta mijoz buyurtmasi
              </div>
            </div>

            <div className="rounded-2xl border border-border bg-card p-4">
              <div className="text-[9px] font-bold uppercase tracking-[.14em] text-[#8a6c43]">
                Xitoy tannarxi (Yuan)
              </div>
              <div className="mt-1 font-display text-[26px] font-medium text-[#8a6c43]">
                ¥{data.total_yuan.toLocaleString()}
              </div>
              <div className="mt-0.5 text-[11px] text-muted-foreground">
                1688 / Taobao / Poizon bo‘yicha
              </div>
            </div>

            <div className="rounded-2xl border border-border bg-card p-4">
              <div className="text-[9px] font-bold uppercase tracking-[.14em] text-muted-foreground">
                Yuan so‘mdagi ekvivalenti
              </div>
              <div className="mt-1 font-display text-[26px] font-medium text-[#172641]">
                {formatPrice(data.total_uzs)}
              </div>
              <div className="mt-0.5 text-[11px] text-muted-foreground">
                O‘zbek so‘mida tannarx
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

          {/* Aggregated China Purchase Table */}
          <div className="overflow-hidden rounded-2xl border border-border bg-card">
            <div className="border-b border-border bg-[#faf8f3] px-5 py-3 flex items-center justify-between">
              <span className="text-xs font-bold text-[#172641]">
                Zakup ro‘yxati (Xitoy kargochisiga yoki postavshikka berish uchun)
              </span>
              <span className="text-[11px] text-muted-foreground">
                Holati: <StatusBadge status={data.status} />
              </span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[800px] text-left text-xs">
                <thead className="bg-[#f6f2e9] text-[9px] font-bold uppercase tracking-[.12em] text-muted-foreground">
                  <tr>
                    <th className="px-5 py-3">Rasm / Model</th>
                    <th className="px-4 py-3">O‘lcham</th>
                    <th className="px-4 py-3">Rang</th>
                    <th className="px-4 py-3 text-center">Soni</th>
                    <th className="px-4 py-3 text-right">Yuan (¥)</th>
                    <th className="px-4 py-3">Buyurtmalar</th>
                    <th className="px-5 py-3">Xitoy havolasi (1688/Taobao)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/70">
                  {data.items.map((it: any, idx: number) => {
                    const supUrl =
                      supplierEdits[it.product_id] !== undefined
                        ? supplierEdits[it.product_id]
                        : it.supplier_url || "";

                    return (
                      <tr key={idx} className="hover:bg-[#faf8f3]/60 transition">
                        <td className="px-5 py-3">
                          <div className="flex items-center gap-3">
                            {it.thumb ? (
                              <img
                                src={`/uploads/${it.thumb}`}
                                alt={it.name}
                                className="h-12 w-10 rounded-lg object-cover border border-border"
                              />
                            ) : (
                              <div className="flex h-12 w-10 items-center justify-center rounded-lg bg-[#eee8db] font-display text-sm text-[#8a6c43]">
                                W
                              </div>
                            )}
                            <div>
                              <div className="font-extrabold text-[13px] text-[#172641]">
                                {it.name}
                              </div>
                              <div className="text-[10px] text-muted-foreground">
                                ID: #{it.product_id}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <span className="rounded-md bg-muted px-2.5 py-1 text-xs font-bold text-[#172641]">
                            {it.size}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-muted-foreground font-semibold">
                          {it.color || "—"}
                        </td>
                        <td className="px-4 py-3 text-center">
                          <span className="inline-flex h-7 min-w-[28px] items-center justify-center rounded-full bg-[#172641] px-2 text-xs font-extrabold text-[#f4efe5]">
                            {it.qty} dona
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right font-mono font-bold text-[#8a6c43]">
                          ¥{(it.price_yuan * it.qty).toLocaleString()}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex flex-wrap gap-1 max-w-[180px]">
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
                        <td className="px-5 py-3">
                          <div className="flex items-center gap-1.5">
                            <input
                              value={supUrl}
                              onChange={(e) =>
                                setSupplierEdits((prev) => ({
                                  ...prev,
                                  [it.product_id]: e.target.value,
                                }))
                              }
                              placeholder="https://detail.1688.com/..."
                              className="wm-input text-[11px] py-1 px-2 h-8 min-w-[190px]"
                            />
                            {supplierEdits[it.product_id] !== undefined && (
                              <button
                                type="button"
                                disabled={savingPid === it.product_id}
                                onClick={() => saveSupplierUrl(it.product_id)}
                                className="wm-btn text-[10px] py-1 px-2.5 h-8 shrink-0"
                              >
                                {savingPid === it.product_id ? "..." : "Saqlash"}
                              </button>
                            )}
                            {supUrl.startsWith("http") && (
                              <a
                                href={supUrl}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center justify-center h-8 px-2 rounded-lg border border-[#172641]/20 bg-[#faf8f3] text-xs font-bold text-[#172641] no-underline hover:bg-[#172641] hover:text-[#f4efe5] transition shrink-0"
                                title="Xitoy saytida ochish"
                              >
                                ↗ Ochish
                              </a>
                            )}
                          </div>
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
        title="💰 Sof Foyda va Xarajatlar"
        detail={`Oxirgi ${days} kundagi tovar tannarxi, kargo va pochta xarajatlari chegirilgan sof foyda tahlili.`}
        action={
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
        }
      />

      {/* 4 Tone Cards for Complete Financial Breakdown */}
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

        {/* Goods Cost in China */}
        <div className="rounded-2xl border border-border bg-card p-5">
          <div className="text-[9px] font-bold uppercase tracking-[.14em] text-[#8a6c43]">
            Xitoy Tovar Tannarxi
          </div>
          <div className="mt-1 font-display text-[26px] font-medium text-[#8a6c43]">
            {formatPrice(data.cost_goods)}
          </div>
          <div className="mt-1 text-[11px] text-muted-foreground">
            Yuan kursi: {data.yuan_rate} so‘m
          </div>
        </div>

        {/* Cargo & Post Shipping */}
        <div className="rounded-2xl border border-border bg-card p-5">
          <div className="text-[9px] font-bold uppercase tracking-[.14em] text-[#397252]">
            Kargo va Pochta Xarajati
          </div>
          <div className="mt-1 font-display text-[26px] font-medium text-[#397252]">
            {formatPrice(data.cost_cargo + data.post_total)}
          </div>
          <div className="mt-1 text-[11px] text-muted-foreground">
            Kargo ({data.shipping_per_kg} so‘m/kg) + BTS/EMU
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
            30% avans va to‘liq to‘langan summalar
          </p>
        </div>

        <div className="rounded-2xl border border-border bg-card p-5">
          <div className="text-xs font-bold text-[#172641]">
            ⏳ Mijozlarning qolgan to‘lovi (Qarzdorlik)
          </div>
          <div className="mt-2 text-xl font-display font-medium text-[#a8742a]">
            {formatPrice(data.debt)}
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground">
            Kiyim kelgach, pochtaga topshirishdan oldin undiriladigan 70%
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

      {/* Top Most Profitable Products Table */}
      <div className="overflow-hidden rounded-2xl border border-border bg-card">
        <div className="border-b border-border bg-[#faf8f3] px-5 py-3">
          <h2 className="text-[13px] font-extrabold text-[#172641]">
            🏆 Eng serdaromad tovarlar reytingi (Sof foyda bo‘yicha)
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#f6f2e9] text-[9px] font-bold uppercase tracking-[.12em] text-muted-foreground">
              <tr>
                <th className="px-5 py-3">Mahsulot nomi</th>
                <th className="px-4 py-3 text-center">Sotilgan soni</th>
                <th className="px-4 py-3 text-right">Tushum</th>
                <th className="px-4 py-3 text-right">Tannarx + Kargo</th>
                <th className="px-5 py-3 text-right">Sof Foyda</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/70">
              {(data.top || []).map((p: any, i: number) => (
                <tr key={i} className="hover:bg-[#faf8f3]/60 transition">
                  <td className="px-5 py-3 font-bold text-[#172641]">
                    {p.name}
                  </td>
                  <td className="px-4 py-3 text-center font-semibold">
                    {p.qty} dona
                  </td>
                  <td className="px-4 py-3 text-right font-medium">
                    {formatPrice(p.revenue)}
                  </td>
                  <td className="px-4 py-3 text-right text-muted-foreground">
                    {formatPrice(p.cost)}
                  </td>
                  <td className="px-5 py-3 text-right font-display text-[14px] font-bold text-[#397252]">
                    +{formatPrice(p.profit)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

