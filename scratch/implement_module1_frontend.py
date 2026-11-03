import os
import re

print("Starting Module 1 Frontend implementation...")

# 1. Update frontend/src/admin/AdminCrmPage.tsx
crm_path = "frontend/src/admin/AdminCrmPage.tsx"
with open(crm_path, "r", encoding="utf-8") as f:
    crm_code = f.read()

# Add fittings tab type and state
if 'activeTab, setActiveTab] = useState<"pipeline" | "tasks">("pipeline")' in crm_code:
    crm_code = crm_code.replace(
        'activeTab, setActiveTab] = useState<"pipeline" | "tasks">("pipeline")',
        'activeTab, setActiveTab] = useState<"pipeline" | "tasks" | "fittings">("pipeline")'
    )

# Add fittings state if not present
if 'fittings, setFittings' not in crm_code:
    crm_code = crm_code.replace(
        '  // Tasks state',
        '''  // Fittings (Primerka) state
  const [fittings, setFittings] = useState<any[]>([]);
  const [loadingFittings, setLoadingFittings] = useState(false);
  const [fittingsStatusFilter, setFittingsStatusFilter] = useState("all");
  const [fittingsDateFilter, setFittingsDateFilter] = useState("");
  const [notifyingFittingId, setNotifyingFittingId] = useState<number | null>(null);

  // Load fittings
  const loadFittings = () => {
    setLoadingFittings(true);
    let url = "/api/admin/crm/fittings";
    const params: string[] = [];
    if (fittingsStatusFilter !== "all") params.push(`status=${fittingsStatusFilter}`);
    if (fittingsDateFilter) params.push(`date=${fittingsDateFilter}`);
    if (params.length > 0) url += `?${params.join("&")}`;

    adminFetch(url)
      .then((res) => {
        setFittings(res.fittings || []);
      })
      .catch((e) => toast(e.message, "error"))
      .finally(() => setLoadingFittings(false));
  };

  const updateFittingStatus = async (fid: number, newStatus: string) => {
    try {
      await adminFetch(`/api/admin/crm/fittings/${fid}`, {
        method: "PUT",
        body: JSON.stringify({ status: newStatus }),
      });
      toast("Primerka holati yangilandi", "success");
      loadFittings();
    } catch (e: any) {
      toast(e.message, "error");
    }
  };

  const notifyFittingCustomer = async (fid: number) => {
    setNotifyingFittingId(fid);
    try {
      const res = await adminFetch(`/api/admin/crm/fittings/${fid}/notify`, {
        method: "POST",
      });
      toast(res.message || "Mijozga Telegramdan eslatma yuborildi", "success");
    } catch (e: any) {
      toast(e.message, "error");
    } finally {
      setNotifyingFittingId(null);
    }
  };

  // Tasks state'''
    )

# Update useEffect to load fittings when activeTab === "fittings"
if 'if (activeTab === "pipeline") {' in crm_code and 'loadFittings()' not in crm_code:
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
    } else if (activeTab === "fittings") {
      loadFittings();
    }
  }, [activeTab, tasksFilter, fittingsStatusFilter, fittingsDateFilter]);'''
    )

# Add tab button in page header
tab_btn_target = '''              <button
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

tab_btn_replacement = tab_btn_target + '''
              <button
                type="button"
                onClick={() => setActiveTab("fittings")}
                className={`rounded-lg px-3.5 py-1.5 text-xs font-bold transition-all cursor-pointer ${
                  activeTab === "fittings"
                    ? "bg-[#172641] text-[#f5f1e8] shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {lang === "ru" ? "🪡 Примерки в ателье" : "🪡 Primerkalar Kalendari"}
              </button>'''

if tab_btn_target in crm_code and 'activeTab === "fittings"' not in crm_code:
    crm_code = crm_code.replace(tab_btn_target, tab_btn_replacement)

# Add Fittings View panel right after tasks view
fittings_view_panel = '''
      {/* ---------------- 2.5 ATELIER FITTINGS & BESPOKE CALENDAR ---------------- */}
      {activeTab === "fittings" && (
        <div className="space-y-4">
          {/* Filters Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-border bg-[#faf8f3] p-4 shadow-sm">
            <div className="flex flex-wrap items-center gap-1.5">
              {[
                { key: "all", label_uz: "Barchasi", label_ru: "Все" },
                { key: "pending", label_uz: "Kutilmoqda", label_ru: "В ожидании" },
                { key: "confirmed", label_uz: "Tasdiqlangan", label_ru: "Подтверждено" },
                { key: "completed", label_uz: "O'tkazildi", label_ru: "Завершено" },
                { key: "cancelled", label_uz: "Bekor qilindi", label_ru: "Отменено" },
              ].map((st) => (
                <button
                  key={st.key}
                  type="button"
                  onClick={() => setFittingsStatusFilter(st.key)}
                  className={`rounded-xl px-3 py-1.5 text-xs font-bold transition cursor-pointer ${
                    fittingsStatusFilter === st.key
                      ? "bg-[#172641] text-[#f5f1e8] shadow-xs"
                      : "bg-white text-muted-foreground border border-border hover:bg-muted"
                  }`}
                >
                  {lang === "ru" ? st.label_ru : st.label_uz}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-muted-foreground">Sana:</span>
              <input
                type="date"
                value={fittingsDateFilter}
                onChange={(e) => setFittingsDateFilter(e.target.value)}
                className="wm-input text-xs py-1.5 px-2.5 max-w-[150px] bg-white"
              />
              {fittingsDateFilter && (
                <button
                  type="button"
                  onClick={() => setFittingsDateFilter("")}
                  className="text-xs text-muted-foreground hover:text-foreground"
                >
                  ✕ Tozalash
                </button>
              )}
            </div>
          </div>

          {/* Appointments Grid */}
          {loadingFittings ? (
            <SkeletonList count={3} />
          ) : fittings.length === 0 ? (
            <EmptyState
              text={
                lang === "ru"
                  ? "Нет запланированных примерок на выбранные параметры"
                  : "Tanlangan parametrlar bo'yicha primerka bronlari mavjud emas"
              }
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {fittings.map((fit: any) => {
                const isPending = fit.status === "pending";
                const isConfirmed = fit.status === "confirmed";
                const isCompleted = fit.status === "completed";

                return (
                  <div
                    key={fit.id}
                    className="flex flex-col justify-between rounded-2xl border border-border bg-white p-4 shadow-sm hover:shadow-md transition-all space-y-3.5"
                  >
                    <div>
                      {/* Top Header: Date, Time & Status */}
                      <div className="flex items-start justify-between gap-2 border-b border-border/70 pb-3">
                        <div>
                          <div className="flex items-center gap-1.5 text-xs font-extrabold text-[#172641]">
                            <span>📅 {fit.appointment_date}</span>
                            <span>·</span>
                            <span>⏰ {fit.appointment_time || "Vaqti belgilanmagan"}</span>
                          </div>
                          <div className="text-[10px] text-muted-foreground mt-0.5">
                            Qayd: #{fit.id} · {fit.created_at ? fit.created_at.slice(0, 16).replace("T", " ") : ""}
                          </div>
                        </div>

                        <span
                          className={`rounded-full px-2.5 py-0.5 text-[10px] font-extrabold uppercase tracking-wider ${
                            isPending
                              ? "bg-amber-100 text-amber-800 border border-amber-300"
                              : isConfirmed
                              ? "bg-blue-100 text-[#172641] border border-blue-300"
                              : isCompleted
                              ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                              : "bg-red-100 text-red-800 border border-red-300"
                          }`}
                        >
                          {fit.status}
                        </span>
                      </div>

                      {/* Customer Info */}
                      <div className="mt-3 space-y-1">
                        <div className="font-extrabold text-[14px] text-foreground flex items-center justify-between">
                          <span>👤 {fit.customer_name}</span>
                          {fit.customer_id && (
                            <button
                              type="button"
                              onClick={() => openDossier(fit.customer_id)}
                              className="text-[10px] font-bold text-[#c5a676] hover:underline cursor-pointer"
                            >
                              Sartorial Dosye →
                            </button>
                          )}
                        </div>
                        <div className="text-xs">
                          <a
                            href={`tel:${fit.customer_phone}`}
                            className="font-semibold text-[#172641] hover:underline"
                          >
                            📞 {fit.customer_phone}
                          </a>
                        </div>
                      </div>

                      {/* Product Preview if available */}
                      {fit.product && (
                        <div className="mt-2.5 flex items-center gap-2.5 rounded-xl border border-border/70 bg-[#faf8f3] p-2">
                          {fit.product.image ? (
                            <img
                              src={fit.product.image}
                              alt=""
                              className="h-10 w-10 rounded-lg object-cover border border-border/60"
                            />
                          ) : (
                            <div className="h-10 w-10 rounded-lg bg-muted flex items-center justify-center text-xs">
                              👔
                            </div>
                          )}
                          <div className="min-w-0 flex-1">
                            <div className="text-xs font-bold text-foreground truncate">
                              {fit.product.title}
                            </div>
                            <div className="text-[11px] font-semibold text-[#c5a676]">
                              {formatPrice(fit.product.price)}
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Customer Measurements if provided */}
                      {(fit.height_cm || fit.weight_kg || fit.fit_preference) && (
                        <div className="mt-2.5 rounded-xl border border-[#c5a676]/30 bg-[#faf6ee] p-2 text-[11px] space-y-0.5">
                          <div className="text-[9px] font-bold uppercase tracking-wider text-[#a4814d]">
                            Qomat Pasporti ma'lumotlari:
                          </div>
                          <div className="text-slate-800 font-medium">
                            {fit.height_cm ? `Bo'y: ${fit.height_cm} sm` : ""}{" "}
                            {fit.weight_kg ? `· Vazn: ${fit.weight_kg} kg` : ""}{" "}
                            {fit.fit_preference ? `· Bichiq: ${fit.fit_preference}` : ""}
                          </div>
                        </div>
                      )}

                      {/* Notes */}
                      {fit.notes && (
                        <div className="mt-2 text-xs italic text-muted-foreground bg-muted/40 p-2 rounded-lg">
                          "{fit.notes}"
                        </div>
                      )}
                    </div>

                    {/* Action Buttons */}
                    <div className="pt-2 border-t border-border flex flex-col gap-2">
                      <div className="flex items-center gap-2">
                        <select
                          value={fit.status}
                          onChange={(e) => updateFittingStatus(fit.id, e.target.value)}
                          className="wm-input text-xs py-1.5 px-2 flex-1 font-semibold bg-white"
                        >
                          <option value="pending">⏳ Kutilmoqda</option>
                          <option value="confirmed">✅ Tasdiqlash</option>
                          <option value="completed">🎉 O'tkazildi</option>
                          <option value="cancelled">❌ Bekor qilish</option>
                        </select>

                        <button
                          type="button"
                          onClick={() => notifyFittingCustomer(fit.id)}
                          disabled={notifyingFittingId === fit.id}
                          className="rounded-xl border border-[#c5a676] bg-[#faf5ea] hover:bg-[#c5a676] hover:text-white px-3 py-1.5 text-xs font-bold text-[#172641] transition cursor-pointer flex items-center gap-1 shrink-0"
                          title="Mijozga Telegram orqali sana va vaqtni eslatish"
                        >
                          {notifyingFittingId === fit.id ? "Yuborilmoqda..." : "📲 Eslatma"}
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
'''

if 'activeTab === "tasks" && (' in crm_code and 'activeTab === "fittings" && (' not in crm_code:
    # Insert fittings view before `{/* ---------------- 3. CUSTOMER 360° SARTORIAL DOSSIER MODAL ---------------- */}`
    crm_code = crm_code.replace(
        '{/* ---------------- 3. CUSTOMER 360° SARTORIAL DOSSIER MODAL ---------------- */}',
        fittings_view_panel + '\n      {/* ---------------- 3. CUSTOMER 360° SARTORIAL DOSSIER MODAL ---------------- */}'
    )

with open(crm_path, "w", encoding="utf-8") as f:
    f.write(crm_code)

print("AdminCrmPage.tsx updated successfully!")

