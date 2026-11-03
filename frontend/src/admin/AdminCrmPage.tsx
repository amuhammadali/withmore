import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { adminFetch } from "../api";
import { formatPrice, useLang } from "../i18n";
import { EmptyState, SkeletonList, useToast } from "../ui";
import { PageHeader } from "./AdminPages";

export function AdminCrmPage() {
  const { lang } = useLang();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState<"pipeline" | "tasks" | "abandoned">("pipeline");

  // Pipeline state
  const [columns, setColumns] = useState<any[]>([]);
  const [loadingPipeline, setLoadingPipeline] = useState(true);
  const [movingId, setMovingId] = useState<number | null>(null);

  // Customer dossier modal state
  const [dossierCid, setDossierCid] = useState<number | null>(null);
  const [dossierData, setDossierData] = useState<any>(null);
  const [loadingDossier, setLoadingDossier] = useState(false);
  const [savingDossier, setSavingDossier] = useState(false);

  // Fittings (Primerka) state
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

  // Abandoned Carts State
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

  // Tasks state
  const [tasks, setTasks] = useState<any[]>([]);
  const [tasksFilter, setTasksFilter] = useState<"pending" | "done">("pending");
  const [loadingTasks, setLoadingTasks] = useState(false);
  const [showNewTaskModal, setShowNewTaskModal] = useState(false);
  const [newTask, setNewTask] = useState({
    customer_id: null as number | null,
    customer_name: "",
    customer_phone: "",
    title: "",
    due_date: new Date().toISOString().split("T")[0],
    assigned_admin_name: "",
  });

  // Load pipeline
  const loadPipeline = () => {
    setLoadingPipeline(true);
    adminFetch("/api/admin/crm/pipeline")
      .then((res) => {
        setColumns(res.columns || []);
      })
      .catch((e) => toast(e.message, "error"))
      .finally(() => setLoadingPipeline(false));
  };

  // Load tasks
  const loadTasks = () => {
    setLoadingTasks(true);
    adminFetch(`/api/admin/crm/tasks?status=${tasksFilter}`)
      .then((res) => {
        setTasks(res.tasks || []);
      })
      .catch((e) => toast(e.message, "error"))
      .finally(() => setLoadingTasks(false));
  };

  useEffect(() => {
    if (activeTab === "pipeline") {
      loadPipeline();
    } else if (activeTab === "tasks") {
      loadTasks();
    } else if (activeTab === "abandoned") {
      loadAbandonedCarts();
    }
  }, [activeTab, tasksFilter]);

  // Move order stage
  const moveStage = async (orderId: number, newStatus: string) => {
    setMovingId(orderId);
    try {
      await adminFetch("/api/admin/crm/pipeline/move", {
        method: "POST",
        body: JSON.stringify({ order_id: orderId, new_status: newStatus }),
      });
      toast(lang === "ru" ? "Статус сделки обновлён" : "Buyurtma bosqichi o'zgartirildi");
      loadPipeline();
    } catch (e: any) {
      toast(e.message, "error");
    } finally {
      setMovingId(null);
    }
  };

  // Open customer dossier
  const openDossier = (cid: number) => {
    setDossierCid(cid);
    setLoadingDossier(true);
    adminFetch(`/api/admin/crm/customer/${cid}`)
      .then((res) => {
        setDossierData(res);
      })
      .catch((e) => toast(e.message, "error"))
      .finally(() => setLoadingDossier(false));
  };

  // Save customer dossier
  const saveDossier = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!dossierCid || !dossierData) return;
    setSavingDossier(true);
    try {
      await adminFetch(`/api/admin/crm/customer/${dossierCid}`, {
        method: "PUT",
        body: JSON.stringify(dossierData.dossier),
      });
      toast(lang === "ru" ? "Досье клиента сохранено" : "Mijoz dosyesi saqlandi!");
    } catch (e: any) {
      toast(e.message, "error");
    } finally {
      setSavingDossier(false);
    }
  };

  // Toggle task
  const toggleTask = async (tid: number) => {
    try {
      await adminFetch(`/api/admin/crm/tasks/${tid}/toggle`, { method: "POST" });
      loadTasks();
    } catch (e: any) {
      toast(e.message, "error");
    }
  };

  // Create new task
  const submitNewTask = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await adminFetch("/api/admin/crm/tasks", {
        method: "POST",
        body: JSON.stringify(newTask),
      });
      toast(lang === "ru" ? "Задача успешно создана" : "Vazifa muvaffaqiyatli qo'shildi");
      setShowNewTaskModal(false);
      setNewTask({
        customer_id: null,
        customer_name: "",
        customer_phone: "",
        title: "",
        due_date: new Date().toISOString().split("T")[0],
        assigned_admin_name: "",
      });
      if (activeTab === "tasks") loadTasks();
    } catch (e: any) {
      toast(e.message, "error");
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow={lang === "ru" ? "Управление взаимоотношениями" : "Mijozlar bilan ishlash"}
        title={lang === "ru" ? "📊 CRM Воронка и Клиенты" : "📊 CRM Voronka & Mijozlar"}
        detail={
          lang === "ru"
            ? "Интерактивная канбан-доска сделок, портрет клиента, индивидуальные размеры и задачи администраторов."
            : "Buyurtmalar voronkasi (Kanban), mijozning 360° kiyim razmerlari dosyesi va admin vazifalari."
        }
        action={
          <div className="flex flex-wrap items-center gap-2">
            <div className="inline-flex rounded-xl border border-border bg-card p-1">
              <button
                type="button"
                onClick={() => setActiveTab("pipeline")}
                className={`rounded-lg px-3.5 py-1.5 text-xs font-bold transition-all cursor-pointer ${
                  activeTab === "pipeline"
                    ? "bg-[#172641] text-[#f5f1e8] shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {lang === "ru" ? "📌 Канбан воронка" : "📌 Kanban Voronkasi"}
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("tasks")}
                className={`rounded-lg px-3.5 py-1.5 text-xs font-bold transition-all cursor-pointer ${
                  activeTab === "tasks"
                    ? "bg-[#172641] text-[#f5f1e8] shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {lang === "ru" ? "⏰ Задачи и звонки" : "⏰ Eslatmalar & Vazifalar"}
              </button>

            </div>
            <button
              type="button"
              onClick={() => {
                setNewTask((prev) => ({ ...prev, customer_name: "", customer_phone: "" }));
                setShowNewTaskModal(true);
              }}
              className="wm-btn text-xs py-2 px-3.5 flex items-center gap-1.5"
            >
              <span>+</span>
              <span>{lang === "ru" ? "Новая задача" : "Yangi vazifa"}</span>
            </button>
          </div>
        }
      />

      {/* ---------------- 1. KANBAN PIPELINE VIEW ---------------- */}
      {activeTab === "pipeline" && (
        <div>
          {loadingPipeline ? (
            <SkeletonList count={4} />
          ) : columns.length === 0 ? (
            <EmptyState text={lang === "ru" ? "Нет активных сделок" : "Hozircha buyurtmalar yo'q"} />
          ) : (
            <div className="flex gap-4 overflow-x-auto pb-6 pt-1 snap-x scrollbar-thin">
              {columns.map((col) => {
                const title = lang === "ru" ? col.title_ru : col.title_uz;
                return (
                  <div
                    key={col.id}
                    className="w-[305px] shrink-0 rounded-2xl border border-border/70 bg-[#faf8f3] flex flex-col max-h-[82vh] snap-start shadow-sm"
                  >
                    {/* Column Header */}
                    <div className="p-3.5 border-b border-border/80 bg-white/70 rounded-t-2xl">
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span
                            className="h-2.5 w-2.5 rounded-full"
                            style={{ backgroundColor: col.color }}
                          />
                          <h3 className="font-extrabold text-[13px] text-[#172641]">
                            {title}
                          </h3>
                        </div>
                        <span className="rounded-full bg-border/60 px-2 py-0.5 text-[11px] font-bold text-foreground">
                          {col.count}
                        </span>
                      </div>
                      <div className="mt-1 text-[11px] font-semibold text-muted-foreground">
                        {formatPrice(col.total_sum)}
                      </div>
                    </div>

                    {/* Column Cards */}
                    <div className="p-2.5 space-y-3 overflow-y-auto flex-1">
                      {col.cards.length === 0 ? (
                        <div className="rounded-xl border border-dashed border-border/80 p-5 text-center text-xs text-muted-foreground">
                          {lang === "ru" ? "Пусто" : "Buyurtma yo'q"}
                        </div>
                      ) : (
                        col.cards.map((c: any) => (
                          <div
                            key={c.id}
                            className={`rounded-xl border border-border bg-white p-3.5 shadow-sm transition-all hover:shadow-md ${
                              movingId === c.id ? "opacity-50 pointer-events-none" : ""
                            }`}
                          >
                            {/* Card Top: Code & Date */}
                            <div className="flex items-center justify-between gap-2 text-xs">
                              <Link
                                to={`/admin/orders/${c.id}`}
                                className="font-mono font-black text-[#172641] hover:underline"
                              >
                                #{c.code}
                              </Link>
                              <span className="text-[10px] text-muted-foreground">
                                {c.created_at.split(" ")[0]}
                              </span>
                            </div>

                            {/* Customer info & Dossier trigger */}
                            <div className="mt-2">
                              <div className="flex items-center justify-between gap-1">
                                <span className="font-bold text-[13px] text-foreground truncate">
                                  {c.customer_name}
                                </span>
                                {c.customer_id && (
                                  <button
                                    type="button"
                                    onClick={() => openDossier(c.customer_id)}
                                    title={
                                      lang === "ru"
                                        ? "Открыть досье и размеры"
                                        : "Mijoz dosyesi va razmerlarini ochish"
                                    }
                                    className="shrink-0 rounded bg-[#f6f2ea] px-1.5 py-0.5 text-[10px] font-bold text-[#806a48] border border-[#d9d3c6] hover:bg-[#172641] hover:text-white transition-colors cursor-pointer"
                                  >
                                    👤 360°
                                  </button>
                                )}
                              </div>
                              <div className="flex items-center gap-2 mt-0.5 text-[11px] text-muted-foreground">
                                {c.phone && (
                                  <a
                                    href={`tel:${c.phone}`}
                                    className="hover:text-primary underline decoration-dotted"
                                  >
                                    {c.phone}
                                  </a>
                                )}
                                {c.tg_username && (
                                  <a
                                    href={`https://t.me/${c.tg_username.replace(/^@/, "")}`}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="text-[#2a75d3] font-medium"
                                  >
                                    @{c.tg_username}
                                  </a>
                                )}
                              </div>
                            </div>

                            {/* Delivery & Items summary */}
                            <div className="mt-2.5 rounded-lg bg-[#f9f8f6] p-2 text-[11px] space-y-1">
                              <div className="text-muted-foreground truncate">
                                📮 {c.city || "O'zbekiston"} · BTS / EMU
                              </div>
                              <div className="font-medium text-foreground truncate">
                                🛍 {c.items_summary}
                              </div>
                              {c.tracking && (
                                <div className="font-mono text-[10px] text-[#2c6e49] font-bold">
                                  Trek: {c.tracking}
                                </div>
                              )}
                            </div>

                            {/* Price & Paid Status */}
                            <div className="mt-3 flex items-baseline justify-between border-t border-border/60 pt-2 text-xs">
                              <div>
                                <span className="text-[10px] text-muted-foreground block">
                                  {lang === "ru" ? "Сумма" : "Summa"}
                                </span>
                                <span className="font-extrabold text-[#172641]">
                                  {formatPrice(c.total)}
                                </span>
                              </div>
                              <div className="text-right">
                                <span className="text-[10px] text-muted-foreground block">
                                  {lang === "ru" ? "Оплачено" : "To'langan"}
                                </span>
                                <span
                                  className={`font-bold ${
                                    c.paid_amount >= c.total
                                      ? "text-[#2c6e49]"
                                      : c.paid_amount > 0
                                      ? "text-[#aa8a5e]"
                                      : "text-muted-foreground"
                                  }`}
                                >
                                  {formatPrice(c.paid_amount)}
                                </span>
                              </div>
                            </div>

                            {/* Quick Stage Mover Selector */}
                            <div className="mt-3 flex items-center justify-between gap-1.5 border-t border-border/50 pt-2">
                              <span className="text-[9px] font-bold uppercase tracking-wider text-muted-foreground">
                                {lang === "ru" ? "Переместить" : "Bosqich"}:
                              </span>
                              <select
                                value={c.status}
                                onChange={(e) => moveStage(c.id, e.target.value)}
                                className="rounded border border-border/80 bg-white py-1 px-1.5 text-[10px] font-bold text-[#172641] cursor-pointer hover:border-primary outline-none max-w-[145px]"
                              >
                                {columns.map((st) => (
                                  <option key={st.id} value={st.id}>
                                    {lang === "ru" ? st.title_ru : st.title_uz}
                                  </option>
                                ))}
                              </select>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ---------------- 2. TASKS & FOLLOW-UPS TAB ---------------- */}
      {activeTab === "tasks" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <div className="inline-flex rounded-lg border border-border bg-card p-1 text-xs font-bold">
              <button
                type="button"
                onClick={() => setTasksFilter("pending")}
                className={`rounded px-3 py-1 cursor-pointer ${
                  tasksFilter === "pending"
                    ? "bg-[#172641] text-white"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {lang === "ru" ? "⏳ Ожидают выполнения" : "⏳ Kutilayotgan vazifalar"}
              </button>
              <button
                type="button"
                onClick={() => setTasksFilter("done")}
                className={`rounded px-3 py-1 cursor-pointer ${
                  tasksFilter === "done"
                    ? "bg-[#172641] text-white"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {lang === "ru" ? "✅ Выполненные" : "✅ Bajarilganlar"}
              </button>
            </div>
          </div>

          {loadingTasks ? (
            <SkeletonList count={3} />
          ) : tasks.length === 0 ? (
            <EmptyState
              text={
                tasksFilter === "pending"
                  ? lang === "ru"
                    ? "Все задачи выполнены!"
                    : "Hozircha faol vazifalar yo'q. Hammasi bajarilgan!"
                  : lang === "ru"
                  ? "Нет выполненных задач"
                  : "Bajarilgan vazifalar tarixi bo'sh"
              }
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {tasks.map((t: any) => (
                <div
                  key={t.id}
                  className={`rounded-2xl border p-4 bg-card shadow-sm space-y-3 ${
                    t.status === "done"
                      ? "border-border/60 opacity-65 bg-[#faf8f3]"
                      : "border-border"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <button
                      type="button"
                      onClick={() => toggleTask(t.id)}
                      className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-md border font-bold text-xs cursor-pointer transition-colors ${
                        t.status === "done"
                          ? "bg-[#2c6e49] text-white border-[#2c6e49]"
                          : "border-border hover:border-primary text-transparent"
                      }`}
                    >
                      ✓
                    </button>
                    <div className="flex-1 min-w-0">
                      <h4
                        className={`text-sm font-bold text-foreground leading-snug ${
                          t.status === "done" ? "line-through text-muted-foreground" : ""
                        }`}
                      >
                        {t.title}
                      </h4>
                      <div className="mt-1 flex flex-wrap items-center gap-2 text-[11px] text-muted-foreground">
                        <span>📅 Muddat: {t.due_date}</span>
                        <span>·</span>
                        <span>👤 {t.assigned_admin_name || "Admin"}</span>
                      </div>
                    </div>
                  </div>

                  {(t.customer_name || t.customer_phone) && (
                    <div className="rounded-xl border border-border/70 bg-[#faf8f3] p-2.5 text-xs flex items-center justify-between gap-2">
                      <div className="truncate">
                        <div className="font-bold text-foreground">
                          {t.customer_name || "Mijoz"}
                        </div>
                        {t.customer_phone && (
                          <a
                            href={`tel:${t.customer_phone}`}
                            className="text-[11px] text-muted-foreground hover:underline"
                          >
                            {t.customer_phone}
                          </a>
                        )}
                      </div>
                      {t.customer_id && (
                        <button
                          type="button"
                          onClick={() => openDossier(t.customer_id)}
                          className="shrink-0 rounded bg-white px-2 py-1 text-[10px] font-bold text-[#806a48] border border-border hover:bg-[#172641] hover:text-white"
                        >
                          Dosye
                        </button>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      
      
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
                            `Salom, ${cart.customer_name}! 👔\n\nWithmore savatingizda siz tanlagan nafis kiyimlar kutmoqda. Buyurtmani yakunlash uchun maxsus 5% chegirma promokodini taqdim etamiz: WITHMORE5`
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
                              `Salom, ${selectedCart.customer_name}! 👔\n\nWithmore savatingizda siz tanlagan nafis kiyimlar kutmoqda. Buyurtmani yakunlash uchun maxsus ${pct}% chegirma promokodini taqdim etamiz: WITHMORE${pct}`
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

      {/* ---------------- 3. CUSTOMER 360° SARTORIAL DOSSIER MODAL ---------------- */}
      {dossierCid && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-[3px] overflow-y-auto">
          <div className="w-full max-w-2xl rounded-2xl border border-border bg-card p-6 shadow-2xl space-y-6 my-6 max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-border pb-4">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-[.2em] text-[#aa8a5e]">
                  WITHMORE SARTORIAL CLUB
                </span>
                <h2 className="text-xl font-display font-medium text-foreground">
                  👤 {dossierData?.customer?.name || "Mijoz Dosyesi"}
                </h2>
                <div className="mt-0.5 text-xs text-muted-foreground">
                  {dossierData?.customer?.phone || ""} · VIP:{" "}
                  <b className="text-[#aa8a5e]">
                    {dossierData?.dossier?.vip_tier || "Standard"}
                  </b>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setDossierCid(null)}
                className="rounded-lg border border-border p-2 text-muted-foreground hover:bg-muted cursor-pointer"
              >
                ✕
              </button>
            </div>

            {loadingDossier ? (
              <SkeletonList count={3} />
            ) : !dossierData ? (
              <div className="p-4 text-center">Yuklanmadi</div>
            ) : (
              <form onSubmit={saveDossier} className="space-y-6">
                {/* LTV & Stats summary */}
                <div className="grid grid-cols-3 gap-2 rounded-xl border border-border bg-[#faf8f3] p-3 text-center text-xs">
                  <div>
                    <span className="text-[10px] text-muted-foreground block uppercase font-bold">
                      Jami xarid (LTV)
                    </span>
                    <span className="text-[13px] font-extrabold text-[#172641]">
                      {formatPrice(dossierData.stats.total_spent)}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-muted-foreground block uppercase font-bold">
                      Buyurtmalar
                    </span>
                    <span className="text-[13px] font-extrabold text-[#172641]">
                      {dossierData.stats.total_orders} ta
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-muted-foreground block uppercase font-bold">
                      Faol kutilayotgan
                    </span>
                    <span className="text-[13px] font-extrabold text-[#aa8a5e]">
                      {dossierData.stats.active_orders} ta
                    </span>
                  </div>
                </div>

                {/* Sartorial Measurements Grid */}
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-[#aa8a5e] mb-3">
                    📏 Shaxsiy Razmerlar va Parametrlar
                  </h3>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    <div>
                      <label className="wm-label text-[11px]">Bo‘yi (sm)</label>
                      <input
                        type="number"
                        placeholder="180"
                        value={dossierData.dossier.height_cm || ""}
                        onChange={(e) =>
                          setDossierData({
                            ...dossierData,
                            dossier: {
                              ...dossierData.dossier,
                              height_cm: e.target.value ? Number(e.target.value) : null,
                            },
                          })
                        }
                        className="wm-input text-xs"
                      />
                    </div>
                    <div>
                      <label className="wm-label text-[11px]">Vazni (kg)</label>
                      <input
                        type="number"
                        placeholder="78"
                        value={dossierData.dossier.weight_kg || ""}
                        onChange={(e) =>
                          setDossierData({
                            ...dossierData,
                            dossier: {
                              ...dossierData.dossier,
                              weight_kg: e.target.value ? Number(e.target.value) : null,
                            },
                          })
                        }
                        className="wm-input text-xs"
                      />
                    </div>
                    <div>
                      <label className="wm-label text-[11px]">Kostyum razmeri</label>
                      <input
                        type="text"
                        placeholder="50 / Drop 6"
                        value={dossierData.dossier.suit_size || ""}
                        onChange={(e) =>
                          setDossierData({
                            ...dossierData,
                            dossier: {
                              ...dossierData.dossier,
                              suit_size: e.target.value,
                            },
                          })
                        }
                        className="wm-input text-xs"
                      />
                    </div>
                    <div>
                      <label className="wm-label text-[11px]">Ko‘ylak yoqasi</label>
                      <input
                        type="text"
                        placeholder="40"
                        value={dossierData.dossier.shirt_collar || ""}
                        onChange={(e) =>
                          setDossierData({
                            ...dossierData,
                            dossier: {
                              ...dossierData.dossier,
                              shirt_collar: e.target.value,
                            },
                          })
                        }
                        className="wm-input text-xs"
                      />
                    </div>
                    <div>
                      <label className="wm-label text-[11px]">Poyabzal razmeri</label>
                      <input
                        type="text"
                        placeholder="42"
                        value={dossierData.dossier.shoe_size || ""}
                        onChange={(e) =>
                          setDossierData({
                            ...dossierData,
                            dossier: {
                              ...dossierData.dossier,
                              shoe_size: e.target.value,
                            },
                          })
                        }
                        className="wm-input text-xs"
                      />
                    </div>
                    <div>
                      <label className="wm-label text-[11px]">Bichimi (Fit)</label>
                      <select
                        value={dossierData.dossier.preferred_fit || "Slim fit"}
                        onChange={(e) =>
                          setDossierData({
                            ...dossierData,
                            dossier: {
                              ...dossierData.dossier,
                              preferred_fit: e.target.value,
                            },
                          })
                        }
                        className="wm-input text-xs"
                      >
                        <option value="Slim fit">Slim Fit</option>
                        <option value="Regular fit">Regular Fit</option>
                        <option value="Classic fit">Classic Fit</option>
                        <option value="Relaxed">Relaxed / Oversize</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Birthday & VIP Tier */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="wm-label text-[11px]">Tug‘ilgan kuni</label>
                    <input
                      type="date"
                      value={dossierData.dossier.birthday || ""}
                      onChange={(e) =>
                        setDossierData({
                          ...dossierData,
                          dossier: {
                            ...dossierData.dossier,
                            birthday: e.target.value,
                          },
                        })
                      }
                      className="wm-input text-xs"
                    />
                  </div>
                  <div>
                    <label className="wm-label text-[11px]">VIP Maqomi</label>
                    <select
                      value={dossierData.dossier.vip_tier || "Standard"}
                      onChange={(e) =>
                        setDossierData({
                          ...dossierData,
                          dossier: {
                            ...dossierData.dossier,
                            vip_tier: e.target.value,
                          },
                        })
                      }
                      className="wm-input text-xs font-bold"
                    >
                      <option value="Standard">Standard Member</option>
                      <option value="Silver Member">Silver Member (2M+)</option>
                      <option value="Gold VIP">Gold VIP (5M+)</option>
                      <option value="Platinum Club">Platinum Club (10M+)</option>
                    </select>
                  </div>
                </div>

                {/* Internal Notes */}
                <div>
                  <label className="wm-label text-[11px]">
                    📝 Menejer va Stilist Izohlari (Ichki xotira)
                  </label>
                  <textarea
                    rows={3}
                    placeholder="Mijoz to'q ko'k ranglarni yoqtiradi, yengi 1 sm uzunroq bo'lishini so'raydi..."
                    value={dossierData.dossier.notes || ""}
                    onChange={(e) =>
                      setDossierData({
                        ...dossierData,
                        dossier: {
                          ...dossierData.dossier,
                          notes: e.target.value,
                        },
                      })
                    }
                    className="wm-input text-xs"
                  />
                </div>

                {/* Modal Footer */}
                <div className="flex items-center justify-between border-t border-border pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setNewTask({
                        customer_id: dossierCid,
                        customer_name: dossierData.customer.name,
                        customer_phone: dossierData.customer.phone,
                        title: `${dossierData.customer.name} bilan bog'lanish`,
                        due_date: new Date().toISOString().split("T")[0],
                        assigned_admin_name: "",
                      });
                      setDossierCid(null);
                      setShowNewTaskModal(true);
                    }}
                    className="wm-btn-outline text-xs py-2 px-3"
                  >
                    + Vazifa qo‘yish
                  </button>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => setDossierCid(null)}
                      className="wm-btn-outline text-xs py-2 px-3"
                    >
                      Bekor qilish
                    </button>
                    <button
                      type="submit"
                      disabled={savingDossier}
                      className="wm-btn text-xs py-2 px-5"
                    >
                      {savingDossier ? "Saqlanmoqda…" : "💾 Saqlash"}
                    </button>
                  </div>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* ---------------- 4. NEW TASK MODAL ---------------- */}
      {showNewTaskModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-[3px]">
          <div className="w-full max-w-md rounded-2xl border border-border bg-card p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="font-extrabold text-base text-foreground">
                ⏰ {lang === "ru" ? "Создать задачу" : "Yangi vazifa / Eslatma"}
              </h3>
              <button
                type="button"
                onClick={() => setShowNewTaskModal(false)}
                className="text-muted-foreground hover:text-foreground text-sm cursor-pointer"
              >
                ✕
              </button>
            </div>

            <form onSubmit={submitNewTask} className="space-y-3.5">
              <div>
                <label className="wm-label text-xs">
                  {lang === "ru" ? "Название задачи" : "Vazifa mazmuni"} *
                </label>
                <input
                  type="text"
                  required
                  placeholder={
                    lang === "ru"
                      ? "Позвонить по размеру костюма..."
                      : "Kastyum razmerini aniqlashtirish uchun telefon qilish..."
                  }
                  value={newTask.title}
                  onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                  className="wm-input text-xs"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="wm-label text-xs">
                    {lang === "ru" ? "Имя клиента" : "Mijoz ismi"}
                  </label>
                  <input
                    type="text"
                    placeholder="Akmal aka"
                    value={newTask.customer_name}
                    onChange={(e) =>
                      setNewTask({ ...newTask, customer_name: e.target.value })
                    }
                    className="wm-input text-xs"
                  />
                </div>
                <div>
                  <label className="wm-label text-xs">
                    {lang === "ru" ? "Телефон" : "Telefon"}
                  </label>
                  <input
                    type="text"
                    placeholder="+998 90 123 45 67"
                    value={newTask.customer_phone}
                    onChange={(e) =>
                      setNewTask({ ...newTask, customer_phone: e.target.value })
                    }
                    className="wm-input text-xs"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="wm-label text-xs">
                    {lang === "ru" ? "Срок выполнения" : "Muddati (Sana)"}
                  </label>
                  <input
                    type="date"
                    required
                    value={newTask.due_date}
                    onChange={(e) => setNewTask({ ...newTask, due_date: e.target.value })}
                    className="wm-input text-xs"
                  />
                </div>
                <div>
                  <label className="wm-label text-xs">
                    {lang === "ru" ? "Ответственный" : "Biriktirilgan admin"}
                  </label>
                  <input
                    type="text"
                    placeholder="Admin"
                    value={newTask.assigned_admin_name}
                    onChange={(e) =>
                      setNewTask({ ...newTask, assigned_admin_name: e.target.value })
                    }
                    className="wm-input text-xs"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-2 border-t border-border pt-3">
                <button
                  type="button"
                  onClick={() => setShowNewTaskModal(false)}
                  className="wm-btn-outline text-xs py-2 px-3.5"
                >
                  {lang === "ru" ? "Отмена" : "Bekor qilish"}
                </button>
                <button type="submit" className="wm-btn text-xs py-2 px-5">
                  {lang === "ru" ? "Сохранить" : "Saqlash"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

