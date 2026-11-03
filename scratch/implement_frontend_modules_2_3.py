import os
import re

print("Starting UI implementation for Abandoned Carts & Unit Economics...")

# 1. Update frontend/src/admin/AdminCrmPage.tsx
crm_path = "frontend/src/admin/AdminCrmPage.tsx"
with open(crm_path, "r", encoding="utf-8") as f:
    crm_code = f.read()

# Update activeTab type
crm_code = crm_code.replace(
    'useState<"pipeline" | "tasks">("pipeline")',
    'useState<"pipeline" | "tasks" | "abandoned">("pipeline")'
)

# Add abandoned cart state and functions
abandoned_state_code = '''  // Abandoned Carts State
  const [abandonedData, setAbandonedData] = useState<any>(null);
  const [loadingAbandoned, setLoadingAbandoned] = useState(false);
  const [selectedCart, setSelectedCart] = useState<any>(null);
  const [recoverDiscount, setRecoverDiscount] = useState<number>(5);
  const [recoverCustomMsg, setRecoverCustomMsg] = useState("");
  const [recovering, setRecovering] = useState(false);

  const loadAbandonedCarts = () => {
    setLoadingAbandoned(true);
    adminFetch("/api/admin/crm/abandoned-carts")
      .then(setAbandonedData)
      .catch((e) => toast(e.message, "error"))
      .finally(() => setLoadingAbandoned(false));
  };

  const handleSendRecovery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCart) return;
    setRecovering(true);
    try {
      const res = await adminFetch(`/api/admin/crm/abandoned-carts/${selectedCart.session_id}/recover`, {
        method: "POST",
        body: JSON.stringify({
          discount_percent: recoverDiscount,
          message: recoverCustomMsg.trim() || undefined,
        }),
      });
      toast(res.message || "Telegramdan eslatma yuborildi", "success");
      setSelectedCart(null);
      setRecoverCustomMsg("");
      loadAbandonedCarts();
    } catch (e: any) {
      toast(e.message, "error");
    } finally {
      setRecovering(false);
    }
  };
'''

if 'abandonedData, setAbandonedData' not in crm_code:
    crm_code = crm_code.replace(
        '  // Tasks state',
        abandoned_state_code + '\n  // Tasks state'
    )

# Update useEffect
crm_code = crm_code.replace(
    '''    if (activeTab === "pipeline") {
      loadPipeline();
    } else {
      loadTasks();
    }
  }, [activeTab, tasksFilter]);''',
    '''    if (activeTab === "pipeline") {
      loadPipeline();
    } else if (activeTab === "tasks") {
      loadTasks();
    } else if (activeTab === "abandoned") {
      loadAbandonedCarts();
    }
  }, [activeTab, tasksFilter]);'''
)

# Add tab button in header
header_btn_target = '''              <button
                type="button"
                onClick={() => setActiveTab("tasks")}
                className={`rounded-lg px-3.5 py-1.5 text-xs font-bold transition-all cursor-pointer ${
                  activeTab === "tasks"
                    ? "bg-[#172641] text-[#f5f1e8] shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {lang === "ru" ? "⏰ Задачи и звонки" : "⏰ Eslatmalar & Vazifalar"}
              </button>'''

header_btn_replacement = header_btn_target + '''
              <button
                type="button"
                onClick={() => setActiveTab("abandoned")}
                className={`rounded-lg px-3.5 py-1.5 text-xs font-bold transition-all cursor-pointer ${
                  activeTab === "abandoned"
                    ? "bg-[#172641] text-[#f5f1e8] shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {lang === "ru" ? "🛒 Брошенные корзины" : "🛒 Tashlab ketilgan savatlar"}
              </button>'''

if header_btn_target in crm_code and 'activeTab === "abandoned"' not in crm_code:
    crm_code = crm_code.replace(header_btn_target, header_btn_replacement)

# Add Abandoned Carts Panel
abandoned_panel_code = '''
      {/* ---------------- 2.8 ABANDONED CARTS & LIVE RADAR VIEW ---------------- */}
      {activeTab === "abandoned" && (
        <div className="space-y-6">
          {/* Top KPI Summary Banner */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="rounded-2xl border border-border bg-[#faf8f3] p-4 shadow-sm">
              <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground block">
                Tashlab ketilgan savatlar
              </span>
              <div className="mt-1 text-2xl font-display font-medium text-[#172641]">
                {abandonedData?.summary?.total_abandoned_count || 0} ta
              </div>
              <p className="text-[11px] text-muted-foreground mt-0.5">
                Kiyim tanlab, buyurtmani yakunlamagan mijozlar
              </p>
            </div>

            <div className="rounded-2xl border border-border bg-[#faf8f3] p-4 shadow-sm">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#aa8a5e] block">
                Savatlardagi jami summa
              </span>
              <div className="mt-1 text-2xl font-display font-medium text-[#aa8a5e]">
                {formatPrice(abandonedData?.summary?.total_abandoned_value || 0)}
              </div>
              <p className="text-[11px] text-muted-foreground mt-0.5">
                Qaytarib olish mumkin bo'lgan sotuv hajmi
              </p>
            </div>

            <div className="rounded-2xl border border-[#172641]/20 bg-[#172641] text-[#f5f1e8] p-4 shadow-sm">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#d6bd92] block">
                Tezkor Qaytarish (1-klikda)
              </span>
              <div className="mt-1 text-sm font-semibold text-[#f5f1e8]">
                Telegram orqali maxsus promo
              </div>
              <p className="text-[11px] text-[#d6bd92]/80 mt-0.5">
                Mijoz botiga to'g'ridan-to'g'ri chegirma yuboriladi
              </p>
            </div>
          </div>

          {/* List of Abandoned Carts */}
          {loadingAbandoned ? (
            <SkeletonList count={3} />
          ) : !abandonedData || abandonedData.abandoned_carts.length === 0 ? (
            <EmptyState
              text="Ayni paytda tashlab ketilgan faol savatlar yo'q. Barcha mijozlar buyurtmani muvaffaqiyatli yakunlagan!"
            />
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {abandonedData.abandoned_carts.map((cart: any) => (
                <div
                  key={cart.session_id}
                  className="rounded-2xl border border-border bg-white p-5 shadow-sm hover:shadow-md transition-all flex flex-col justify-between space-y-4"
                >
                  <div className="space-y-3">
                    {/* Header: Customer and Timestamp */}
                    <div className="flex items-start justify-between gap-2 border-b border-border/70 pb-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-extrabold text-sm text-[#172641]">
                            👤 {cart.customer_name}
                          </span>
                          {cart.customer_id && (
                            <button
                              type="button"
                              onClick={() => openDossier(cart.customer_id)}
                              className="text-[10px] font-bold text-[#aa8a5e] hover:underline cursor-pointer"
                            >
                              Dosye →
                            </button>
                          )}
                        </div>
                        <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground mt-0.5">
                          {cart.customer_phone && (
                            <a
                              href={`tel:${cart.customer_phone}`}
                              className="font-medium text-[#172641] hover:underline"
                            >
                              📞 {cart.customer_phone}
                            </a>
                          )}
                          {cart.tg_username && (
                            <a
                              href={`https://t.me/${cart.tg_username}`}
                              target="_blank"
                              rel="noreferrer"
                              className="text-blue-600 hover:underline"
                            >
                              @{cart.tg_username}
                            </a>
                          )}
                        </div>
                      </div>

                      <div className="text-right">
                        <span className="rounded-full bg-amber-50 border border-amber-200 px-2.5 py-0.5 text-[10px] font-extrabold text-amber-800">
                          {cart.last_action}
                        </span>
                        <div className="text-[10px] text-muted-foreground mt-1">
                          {cart.last_seen ? cart.last_seen.slice(0, 16).replace("T", " ") : ""}
                        </div>
                      </div>
                    </div>

                    {/* Products in Cart */}
                    <div className="space-y-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                        Savatdagi mahsulotlar ({cart.items_count} dona):
                      </span>
                      <div className="space-y-1.5">
                        {cart.items.map((item: any, idx: number) => (
                          <div
                            key={idx}
                            className="flex items-center justify-between gap-3 rounded-xl border border-border/60 bg-[#faf8f3] p-2 text-xs"
                          >
                            <div className="flex items-center gap-2.5 min-w-0">
                              {item.image ? (
                                <img
                                  src={item.image}
                                  alt=""
                                  className="h-10 w-10 rounded-lg object-cover border border-border/60 shrink-0"
                                />
                              ) : (
                                <div className="h-10 w-10 rounded-lg bg-muted flex items-center justify-center text-xs shrink-0">
                                  👔
                                </div>
                              )}
                              <div className="truncate">
                                <div className="font-bold text-foreground truncate">
                                  {item.title}
                                </div>
                                <div className="text-[11px] text-muted-foreground">
                                  {item.size ? `O'lcham: ${item.size}` : ""} {item.color ? `· ${item.color}` : ""} · {item.qty} dona
                                </div>
                              </div>
                            </div>
                            <div className="font-bold text-[#172641] shrink-0 text-right">
                              {formatPrice(item.total)}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Footer: Total and Action */}
                  <div className="border-t border-border pt-3 flex items-center justify-between gap-2">
                    <div>
                      <span className="text-[10px] text-muted-foreground uppercase font-bold block">
                        Savat qiymati:
                      </span>
                      <span className="text-base font-extrabold text-[#aa8a5e]">
                        {formatPrice(cart.cart_total)}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      {cart.recovery_sent && (
                        <span className="text-[11px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-xl flex items-center gap-1">
                          ✓ Eslatma yuborilgan
                        </span>
                      )}
                      <button
                        type="button"
                        onClick={() => {
                          setSelectedCart(cart);
                          setRecoverCustomMsg(
                            `Salom, ${cart.customer_name}! 👔\\n\\nWithmore savatingizda siz tanlagan nafis kiyimlar kutmoqda. Buyurtmani yakunlash uchun maxsus 5% chegirma promokodini taqdim etamiz: WITHMORE5`
                          );
                        }}
                        className="rounded-xl border border-[#172641] bg-[#172641] hover:bg-[#23385e] text-[#f5f1e8] px-3.5 py-2 text-xs font-bold transition shadow-xs cursor-pointer flex items-center gap-1.5"
                      >
                        <span>📲</span>
                        <span>Chegirma bilan qaytarish</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Recovery Modal */}
          {selectedCart && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
              <div className="w-full max-w-md rounded-2xl border border-border bg-[#faf8f3] p-6 shadow-2xl text-slate-900 space-y-4 rise-in">
                <div className="flex items-center justify-between border-b border-[#172641]/10 pb-3">
                  <div>
                    <span className="text-[9px] font-bold uppercase tracking-[.2em] text-[#aa8a5e]">
                      TELEGRAM AVTOMATIK QAYTARISH
                    </span>
                    <h3 className="font-display text-lg font-bold text-[#172641]">
                      Mijozga chegirma va eslatma yuborish
                    </h3>
                  </div>
                  <button
                    type="button"
                    onClick={() => setSelectedCart(null)}
                    className="rounded-lg p-1 text-slate-500 hover:text-slate-900 cursor-pointer"
                  >
                    ✕
                  </button>
                </div>

                <div className="rounded-xl border border-border bg-white p-3 text-xs space-y-1">
                  <div className="font-bold text-foreground">
                    👤 Qabul qiluvchi: {selectedCart.customer_name}
                  </div>
                  <div className="text-muted-foreground">
                    Savat qiymati: <b>{formatPrice(selectedCart.cart_total)}</b> ({selectedCart.items_count} ta mahsulot)
                  </div>
                </div>

                <form onSubmit={handleSendRecovery} className="space-y-4">
                  <div>
                    <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-700 mb-1">
                      Chegirma foizi (Promokod)
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      {[5, 10, 15].map((pct) => (
                        <button
                          key={pct}
                          type="button"
                          onClick={() => {
                            setRecoverDiscount(pct);
                            setRecoverCustomMsg(
                              `Salom, ${selectedCart.customer_name}! 👔\\n\\nWithmore savatingizda siz tanlagan nafis kiyimlar kutmoqda. Buyurtmani yakunlash uchun maxsus ${pct}% chegirma promokodini taqdim etamiz: WITHMORE${pct}`
                            );
                          }}
                          className={`rounded-xl py-2 text-xs font-bold transition cursor-pointer border ${
                            recoverDiscount === pct
                              ? "bg-[#172641] text-[#f5f1e8] border-[#172641]"
                              : "bg-white text-slate-700 border-border hover:bg-slate-50"
                          }`}
                        >
                          -{pct}% chegirma
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-700 mb-1">
                      Telegram xabar matni
                    </label>
                    <textarea
                      rows={4}
                      value={recoverCustomMsg}
                      onChange={(e) => setRecoverCustomMsg(e.target.value)}
                      className="w-full rounded-xl border border-[#172641]/20 bg-white p-3 text-xs text-slate-900 font-medium"
                      placeholder="Xabar matnini kiriting..."
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={recovering}
                    className="w-full rounded-xl bg-[#172641] py-3 text-xs font-bold uppercase tracking-wider text-[#faf7f2] shadow-md hover:bg-[#23385e] transition cursor-pointer"
                  >
                    {recovering ? "Yuborilmoqda..." : "🚀 Telegram orqali yuborish"}
                  </button>
                </form>
              </div>
            </div>
          )}
        </div>
      )}
'''

if '{/* ---------------- 3. CUSTOMER 360° SARTORIAL DOSSIER MODAL ---------------- */}' in crm_code:
    crm_code = crm_code.replace(
        '{/* ---------------- 3. CUSTOMER 360° SARTORIAL DOSSIER MODAL ---------------- */}',
        abandoned_panel_code + '\n      {/* ---------------- 3. CUSTOMER 360° SARTORIAL DOSSIER MODAL ---------------- */}'
    )

with open(crm_path, "w", encoding="utf-8") as f:
    f.write(crm_code)
print("AdminCrmPage.tsx updated with Abandoned Carts UI!")

# 2. Update frontend/src/admin/AdminOpsPages.tsx with enhanced Unit Economics
ops_ui_path = "frontend/src/admin/AdminOpsPages.tsx"
with open(ops_ui_path, "r", encoding="utf-8") as f:
    ops_ui = f.read()

# Add Unit Economics table & settings modal in FinanceProfitPage
table_marker = '{/* Top Most Profitable Products Table */}'
unit_economics_table = '''      {/* Order-by-Order Real Net Profit (Unit Economics Breakdown) */}
      <div className="overflow-hidden rounded-2xl border border-border bg-card">
        <div className="border-b border-border bg-[#faf8f3] px-5 py-3 flex items-center justify-between">
          <div>
            <h2 className="text-[13px] font-extrabold text-[#172641]">
              🧾 Har bir buyurtma bo‘yicha sof foyda tahlili (Unit Economics)
            </h2>
            <div className="text-[11px] text-muted-foreground mt-0.5">
              Har bir buyurtmaning tushumi, Xitoydan tannarxi (COGS), kargo va yetkazib berishdan keyingi aniq sof foydasi.
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
                <th className="px-4 py-3 text-right">Tannarx (Xitoy)</th>
                <th className="px-4 py-3 text-right">Kargo & Pochta</th>
                <th className="px-5 py-3 text-right">Haqiqiy Sof Foyda</th>
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
                    <td className="px-4 py-3 text-[11px] text-slate-700 max-w-[200px] truncate">
                      {ord.items_summary}
                    </td>
                    <td className="px-4 py-3 text-right font-medium">
                      {formatPrice(ord.revenue)}
                    </td>
                    <td className="px-4 py-3 text-right text-muted-foreground">
                      {formatPrice(ord.cogs)}
                    </td>
                    <td className="px-4 py-3 text-right text-muted-foreground">
                      {formatPrice(ord.cargo + ord.delivery)}
                    </td>
                    <td className="px-5 py-3 text-right font-display text-[13px] font-bold">
                      <span
                        className={`inline-block px-2.5 py-0.5 rounded-full ${
                          isPositive
                            ? "bg-emerald-100 text-emerald-800"
                            : "bg-red-100 text-red-800"
                        }`}
                      >
                        {isPositive ? "+" : ""}{formatPrice(ord.profit)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className="font-extrabold text-[11px] text-[#aa8a5e]">
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

'''

if table_marker in ops_ui and 'Order-by-Order Real Net Profit' not in ops_ui:
    ops_ui = ops_ui.replace(table_marker, unit_economics_table + '\n      ' + table_marker)

# Add Settings Drawer in FinanceProfitPage
settings_btn_target = '<div className="flex rounded-xl border border-border bg-card p-1">'
settings_btn_code = '''<div className="flex items-center gap-2">
            <div className="rounded-xl border border-border bg-[#faf8f3] px-3 py-1.5 text-xs text-[#172641] flex items-center gap-3">
              <span>🇨🇳 1¥ = <b>{data.yuan_rate} so'm</b></span>
              <span>✈️ 1kg = <b>{formatPrice(data.shipping_per_kg)}</b></span>
            </div>
            <div className="flex rounded-xl border border-border bg-card p-1">'''

if settings_btn_target in ops_ui and '1¥ = <b>' not in ops_ui:
    ops_ui = ops_ui.replace(settings_btn_target, settings_btn_code)
    # close the extra div
    ops_ui = ops_ui.replace('))}          </div>        }', '))}          </div>        </div>}')

with open(ops_ui_path, "w", encoding="utf-8") as f:
    f.write(ops_ui)
print("AdminOpsPages.tsx updated with Unit Economics breakdown!")

