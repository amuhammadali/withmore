import React, { useEffect, useState } from "react";
import { Link, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { adminFetch, setCsrf } from "../api";
import { useLang } from "../i18n";
import { LangSwitcher, useToast } from "../ui";
import {
  AuditPage,
  CategoriesPage,
  ContentPage,
  CustomersPage,
  DashboardPage,
  GrowthPage,
  BroadcastPage,
  MarketingPage,
  OrderDetailPage,
  OrdersPage,
  ProductFormPage,
  ProductsPage,
  PromotionsPage,
  SettingsPage,
  TeamPage,
} from "./AdminPages";
import { ChinaProcurementPage, FinanceProfitPage } from "./AdminOpsPages";
import { AdminCrmPage } from "./AdminCrmPage";

interface NavItemDef {
  to: string;
  labelUz: string;
  labelRu: string;
  subUz: string;
  subRu: string;
  exact?: boolean;
  perm: string;
  icon: string;
}

const NAV_DEFS: NavItemDef[] = [
  {
    to: "/admin",
    labelUz: "Umumiy ko‘rinish",
    labelRu: "Обзор",
    subUz: "Statistika",
    subRu: "Статистика",
    exact: true,
    perm: "statistics",
    icon: "M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z",
  },
  {
    to: "/admin/products",
    labelUz: "Mahsulotlar",
    labelRu: "Товары",
    subUz: "Katalog",
    subRu: "Каталог",
    perm: "products",
    icon: "M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4",
  },
  {
    to: "/admin/orders",
    labelUz: "Buyurtmalar",
    labelRu: "Заказы",
    subUz: "Mijozlar buyurtmalari",
    subRu: "Заказы клиентов",
    perm: "orders",
    icon: "M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2",
  },
  {
    to: "/admin/crm",
    labelUz: "📊 CRM Voronka",
    labelRu: "📊 CRM Воронка",
    subUz: "Pipeline & Razmerlar",
    subRu: "Сделки и задачи",
    perm: "orders",
    icon: "M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2",
  },
  {
    to: "/admin/broadcast",
    labelUz: "📢 Telegram Broadcast",
    labelRu: "📢 Рассылка клиентам",
    subUz: "Xabarnoma yuborish",
    subRu: "Telegram рассылка",
    perm: "orders",
    icon: "M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z",
  },
  {
    to: "/admin/china",
    labelUz: "🇨🇳 Xitoy Zakup",
    labelRu: "🇨🇳 Закупки в Китае",
    subUz: "Ta’minot",
    subRu: "Закупки",
    perm: "orders",
    icon: "M16 11V7a4 4 0 0 0-8 0v4M5 9h14l1 12H4L5 9z",
  },
  {
    to: "/admin/finance",
    labelUz: "💰 Sof Foyda",
    labelRu: "💰 Чистая прибыль",
    subUz: "Moliya",
    subRu: "Финансы",
    perm: "statistics",
    icon: "M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6",
  },
  {
    to: "/admin/customers",
    labelUz: "Mijozlar",
    labelRu: "Клиенты",
    subUz: "Baza",
    subRu: "База клиентов",
    perm: "customers",
    icon: "M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z",
  },
  {
    to: "/admin/promotions",
    labelUz: "Aksiyalar",
    labelRu: "Акции и промокоды",
    subUz: "Chegirmalar",
    subRu: "Скидки",
    perm: "promotions",
    icon: "M7 7h.01M3 3h7l11 11-7 7L3 10V3z",
  },
  {
    to: "/admin/settings",
    labelUz: "Sozlamalar",
    labelRu: "Настройки",
    subUz: "Tizim",
    subRu: "Система",
    perm: "settings",
    icon: "M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9",
  },
  {
    to: "/admin/marketing",
    labelUz: "📈 Reklama & UTM",
    labelRu: "📈 Реклама и UTM",
    subUz: "Trafik tahlili",
    subRu: "Анализ источников",
    perm: "statistics",
    icon: "M18 20V10M12 20V4M6 20v-6",
  },
  {
    to: "/admin/growth",
    labelUz: "O‘sish",
    labelRu: "Рост",
    subUz: "Analitika",
    subRu: "Аналитика",
    perm: "owner",
    icon: "M23 6l-9.5 9.5-5-5L1 18M17 6h6v6",
  },
  {
    to: "/admin/content",
    labelUz: "Vitrina",
    labelRu: "Витрина",
    subUz: "Bannerlar",
    subRu: "Баннеры",
    perm: "owner",
    icon: "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6",
  },
  {
    to: "/admin/team",
    labelUz: "Jamoa",
    labelRu: "Команда",
    subUz: "Xodimlar",
    subRu: "Сотрудники",
    perm: "owner",
    icon: "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z",
  },
  {
    to: "/admin/audit",
    labelUz: "Faoliyat",
    labelRu: "Журнал действий",
    subUz: "Audit",
    subRu: "Аудит",
    perm: "owner",
    icon: "M12 8v4l3 3m6-3a9 9 0 1 1-18 0 9 9 0 0 1 18 0z",
  },
];

export function AdminRoot() {
  const { t, lang } = useLang();
  const { toast } = useToast();
  const location = useLocation();
  const [admin, setAdmin] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [tgLinkInfo, setTgLinkInfo] = useState<{ url?: string; token?: string; bot_username?: string } | null>(null);
  const [tgLoading, setTgLoading] = useState(false);

  const refreshMe = () => {
    adminFetch("/api/admin/me")
      .then((res) => {
        setAdmin(res.admin);
        setCsrf(res.csrf);
      })
      .catch(() => setAdmin(null))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    refreshMe();
  }, []);

  useEffect(() => {
    if (!tgLinkInfo || admin?.telegram_linked) return;
    const timer = window.setInterval(() => {
      refreshMe();
    }, 3000);
    return () => window.clearInterval(timer);
  }, [tgLinkInfo, admin?.telegram_linked]);

  if (loading) {
    return (
      <div className="min-h-[100dvh] bg-background p-8">
        <div className="mx-auto max-w-6xl animate-pulse space-y-5">
          <div className="h-10 w-56 rounded-xl bg-muted" />
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div className="h-36 rounded-2xl bg-muted" />
            <div className="h-36 rounded-2xl bg-muted" />
            <div className="h-36 rounded-2xl bg-muted" />
          </div>
          <div className="h-72 rounded-2xl bg-muted" />
        </div>
      </div>
    );
  }

  if (!admin) {
    return (
      <LoginScreen
        onLoggedIn={(a, csrf) => {
          setCsrf(csrf);
          setAdmin(a);
        }}
      />
    );
  }

  const perms: string[] = admin.permissions || [];
  const isOwner = admin.role === "owner";
  const can = (p: string) => {
    if (!p) return true;
    if (p === "owner") return isOwner;
    return isOwner || perms.includes(p);
  };

  const navItems = NAV_DEFS.map((it) => ({
    ...it,
    label: lang === "ru" ? it.labelRu : it.labelUz,
    sub: lang === "ru" ? it.subRu : it.subUz,
  }));

  const visibleNav = navItems.filter((it) => can(it.perm));
  const defaultRoute = visibleNav[0]?.to || "/admin/orders";

  const activeNav =
    visibleNav.find((it) =>
      it.exact
        ? location.pathname === it.to || location.pathname === it.to + "/"
        : location.pathname.startsWith(it.to)
    ) || visibleNav[0] || navItems[0];

  const logout = async () => {
    try {
      await adminFetch("/api/admin/logout", { method: "POST" });
    } catch {
      // ignore
    }
    setAdmin(null);
  };

  const generateTgLink = async () => {
    setTgLoading(true);
    try {
      const r = await adminFetch("/api/admin/me/telegram-link", {
        method: "POST",
      });
      setTgLinkInfo(r);
      const linkText = r.url || `/start link_${r.token}`;
      navigator.clipboard?.writeText(linkText);
      if (r.url) {
        window.open(r.url, "_blank", "noopener");
      }
      toast(
        r.url
          ? `Telegram havola: ${r.url}`
          : `Botda yuboring: /start link_${r.token}`
      );
    } catch (e: any) {
      toast(e.message, "error");
    } finally {
      setTgLoading(false);
    }
  };

  const SidebarContent = (
    <div className="flex h-full flex-col bg-[#172641] text-[#f5f1e8]">
      {/* Brand Header */}
      <div className="flex min-h-[88px] items-center gap-3.5 border-b border-white/10 px-5">
        <img
          src="/whitmore-logo.jpg"
          alt="Withmore"
          onError={(e) => {
            (e.currentTarget as HTMLImageElement).style.display = "none";
          }}
          className="h-12 w-12 shrink-0 rounded-full border border-[#d8c5a6]/50 object-cover shadow-md"
        />
        <div className="min-w-0 leading-none">
          <div className="font-display text-[15px] font-semibold tracking-[.16em] text-white">
            WITHMORE
          </div>
          <div className="mt-1 text-[8px] font-semibold uppercase tracking-[.22em] text-white/50">
            {t.adminPanel || "Classic Menswear"}
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto pb-6">
        <div className="px-6 pt-6 pb-2.5 text-[9px] font-bold uppercase tracking-[.18em] text-white/40">
          Boshqaruv / Workspace
        </div>
        <nav className="space-y-0.5 px-3" aria-label="Asosiy menyu">
          {visibleNav.map((it) => {
            const isActive = it.exact
              ? location.pathname === it.to || location.pathname === it.to + "/"
              : location.pathname.startsWith(it.to);
            return (
              <Link
                key={it.to}
                to={it.to}
                onClick={() => setMobileMenuOpen(false)}
                className={`group flex w-full items-center gap-3 rounded-lg px-3.5 py-2.5 text-left no-underline transition-all duration-150 ${
                  isActive
                    ? "border-l-2 border-[#c5a776] bg-[#293853] text-white"
                    : "border-l-2 border-transparent text-white/70 hover:bg-white/[.04] hover:text-white"
                }`}
              >
                <svg
                  width="15"
                  height="15"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.75"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className={
                    isActive
                      ? "text-[#d6bd92] shrink-0"
                      : "text-white/55 group-hover:text-white/80 shrink-0"
                  }
                >
                  <path d={it.icon} />
                </svg>
                <span className="flex-1 truncate">
                  <span className="block text-[12px] font-medium leading-tight">
                    {it.label}
                  </span>
                  <span className="block text-[9px] text-white/35">
                    {it.sub}
                  </span>
                </span>
              </Link>
            );
          })}
        </nav>

        {/* Telegram Link Compact Card */}
        <div className="mx-3 mt-4 rounded-xl border border-white/10 bg-white/[.035] p-4">
          <div className="flex items-center gap-2 text-[10px] font-semibold text-[#e9e2d4]">
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                admin.telegram_linked ? "bg-[#94ab92]" : "bg-[#c8ac7f]"
              }`}
            />
            {admin.telegram_linked
              ? `${lang === "ru" ? "Telegram подключён" : "Telegram ulangan"}${
                  admin.tg_username ? ` · @${admin.tg_username}` : ""
                }`
              : lang === "ru"
              ? "Telegram не подключён"
              : "Telegram ulanmagan"}
          </div>
          <p className="mt-1.5 text-[10px] leading-[1.6] text-white/50">
            {lang === "ru"
              ? "Привяжите аккаунт, чтобы получать уведомления о новых заказах через Telegram бота."
              : "Yangi buyurtma xabarnomalarini bot orqali olish uchun hisobingizni ulang."}
          </p>
          <button
            type="button"
            onClick={generateTgLink}
            disabled={tgLoading}
            className="mt-2.5 inline-flex items-center gap-1.5 text-[10px] font-bold text-[#d6bd92] cursor-pointer bg-transparent border-0 p-0 disabled:opacity-50"
          >
            <svg
              width="11"
              height="11"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
            </svg>
            {tgLoading
              ? (lang === "ru" ? "Формирование ссылки…" : "Havola tayyorlanmoqda…")
              : admin.telegram_linked
              ? (lang === "ru" ? "Привязать заново" : "Qayta ulash")
              : (lang === "ru" ? "Привязать Telegram" : t.linkTelegram)}
          </button>
          {tgLinkInfo && (
            <div className="mt-2.5 space-y-1.5 border-t border-white/10 pt-2">
              {tgLinkInfo.url ? (
                <a
                  href={tgLinkInfo.url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center justify-center gap-1.5 rounded-lg bg-[#d6bd92] px-3 py-2 text-[10px] font-bold text-[#172641] no-underline shadow-sm hover:opacity-95"
                >
                  @{tgLinkInfo.bot_username || "bot"} {lang === "ru" ? "открыть и нажать Start ↗" : "ni ochish va Start bosish ↗"}
                </a>
              ) : (
                <p className="break-all text-[9px] text-white/60">
                  {lang === "ru" ? "Отправьте боту в Telegram: " : "Telegram botda yuboring: "}
                  <code className="text-[#d6bd92]">/start link_{tgLinkInfo.token}</code>
                </p>
              )}
            </div>
          )}
        </div>

        {/* Storefront & Lang quick bar */}
        <div className="mx-3 mt-3 flex items-center justify-between gap-2 rounded-xl border border-white/10 bg-white/[.02] px-3 py-2">
          <LangSwitcher />
          <Link
            to="/miniapp"
            className="inline-flex items-center gap-1 text-[10px] font-bold text-[#d6bd92] no-underline hover:underline"
          >
            Mini App ↗
          </Link>
        </div>
      </div>

      {/* Sign out footer */}
      <div className="border-t border-white/10 p-3">
        <button
          type="button"
          onClick={logout}
          className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-[11px] font-medium text-white/55 transition hover:bg-white/[.04] hover:text-white cursor-pointer bg-transparent border-0"
        >
          <svg
            width="13"
            height="13"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9" />
          </svg>
          {lang === "ru" ? "Выйти из системы" : t.signOut}
        </button>
      </div>
    </div>
  );

  return (
    <div className="grain min-h-[100dvh] bg-background text-foreground">
      {/* Desktop Fixed Sidebar */}
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-[252px] lg:block">
        {SidebarContent}
      </aside>

      {/* Mobile Drawer Sidebar */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-50 bg-black/50 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        >
          <aside
            className="h-full w-[264px]"
            onClick={(e) => e.stopPropagation()}
          >
            {SidebarContent}
          </aside>
        </div>
      )}

      {/* Main Workspace */}
      <div className="lg:pl-[252px]">
        {/* Static Top Header (not sticky/floating to prevent scroll jitter) */}
        <header className="static z-20 flex min-h-[64px] items-center justify-between gap-4 border-b border-[#e7e2d8] bg-[#fcfbf8] px-5 lg:px-10">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setMobileMenuOpen((v) => !v)}
              aria-label={lang === "ru" ? "Открыть меню" : "Menyuni ochish"}
              className="rounded-lg border border-border p-2 lg:hidden cursor-pointer bg-card"
            >
              <svg
                width="17"
                height="17"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                {mobileMenuOpen ? (
                  <path d="M18 6L6 18M6 6l12 12" />
                ) : (
                  <path d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
            <div>
              <div className="text-[9px] font-bold uppercase tracking-[.22em] text-muted-foreground">
                WITHMORE / {activeNav?.sub ?? (lang === "ru" ? "Панель" : "Workspace")}
              </div>
              <div className="text-[13px] font-bold text-foreground">
                {activeNav?.label ?? (lang === "ru" ? "Управление" : "Boshqaruv")}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <LangSwitcher />
            <Link
              to="/miniapp"
              className="hidden items-center gap-2 rounded-full border border-[#e3ddd0] bg-[#f6f3ec] px-3.5 py-1.5 text-[11px] font-medium text-[#5c6470] no-underline hover:border-[#172641] sm:flex"
            >
              <span className="h-1.5 w-1.5 rounded-full bg-[#4a7c59]" />
              {lang === "ru" ? "Магазин активен" : "Do‘kon faol"}
            </Link>
            <div className="flex items-center gap-2.5 pl-1">
              <div className="flex h-9 w-9 items-center justify-center rounded-full border border-[#a58b65] bg-transparent font-display text-[13px] font-medium text-[#806a48]">
                {(admin.full_name || "A").slice(0, 1).toUpperCase()}
              </div>
              <div className="hidden text-left leading-tight sm:block">
                <div className="text-[12px] font-bold">{admin.full_name}</div>
                <div className="text-[10px] text-muted-foreground">
                  {admin.role === "owner"
                    ? (lang === "ru" ? "Владелец" : "Ega")
                    : (lang === "ru" ? "Администратор" : "Admin")} · @
                  {admin.login || admin.tg_username || "admin"}
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Page Container */}
        <main className="mx-auto max-w-[1440px] px-5 py-7 pb-24 lg:px-10 lg:py-9">
          <Routes>
            <Route
              index
              element={
                can("statistics") ? (
                  <DashboardPage adminName={admin.full_name} />
                ) : (
                  <Navigate to={defaultRoute} replace />
                )
              }
            />
            <Route
              path="dashboard"
              element={
                can("statistics") ? (
                  <DashboardPage adminName={admin.full_name} />
                ) : (
                  <PermissionDenied />
                )
              }
            />
            <Route
              path="products"
              element={
                can("products") ? <ProductsPage /> : <PermissionDenied />
              }
            />
            <Route
              path="products/new"
              element={
                can("products") ? <ProductFormPage /> : <PermissionDenied />
              }
            />
            <Route
              path="products/:id"
              element={
                can("products") ? <ProductFormPage /> : <PermissionDenied />
              }
            />
            <Route
              path="categories"
              element={
                can("products") ? <CategoriesPage /> : <PermissionDenied />
              }
            />
            <Route
              path="orders"
              element={can("orders") ? <OrdersPage /> : <PermissionDenied />}
            />
            <Route
              path="orders/:id"
              element={
                can("orders") ? <OrderDetailPage /> : <PermissionDenied />
              }
            />
            <Route
              path="crm"
              element={can("orders") ? <AdminCrmPage /> : <PermissionDenied />}
            />
            <Route
              path="china"
              element={
                can("orders") ? <ChinaProcurementPage /> : <PermissionDenied />
              }
            />
            <Route
              path="finance"
              element={
                can("statistics") ? <FinanceProfitPage /> : <PermissionDenied />
              }
            />
            <Route
              path="customers"
              element={
                can("customers") ? <CustomersPage /> : <PermissionDenied />
              }
            />
            <Route
              path="promotions"
              element={
                can("promotions") ? <PromotionsPage /> : <PermissionDenied />
              }
            />
            <Route
              path="broadcast"
              element={<BroadcastPage />}
            />
            <Route
              path="marketing"
              element={<MarketingPage />}
            />
            <Route
              path="growth"
              element={can("owner") ? <GrowthPage /> : <PermissionDenied />}
            />
            <Route
              path="settings"
              element={
                can("settings") ? <SettingsPage /> : <PermissionDenied />
              }
            />
            <Route
              path="team"
              element={can("owner") ? <TeamPage /> : <PermissionDenied />}
            />
            <Route
              path="content"
              element={can("owner") ? <ContentPage /> : <PermissionDenied />}
            />
            <Route
              path="audit"
              element={can("owner") ? <AuditPage /> : <PermissionDenied />}
            />
            <Route
              path="activity"
              element={can("owner") ? <AuditPage /> : <PermissionDenied />}
            />
            <Route path="*" element={<Navigate to={defaultRoute} replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

function PermissionDenied() {
  return (
    <div className="mx-auto max-w-md rounded-2xl border border-border bg-card px-6 py-14 text-center rise-in">
      <svg
        width="26"
        height="26"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#aa8a5e"
        strokeWidth="1.8"
        className="mx-auto"
      >
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      </svg>
      <h2 className="mt-3 text-[15px] font-extrabold">Ruxsat yo‘q</h2>
      <p className="mt-1 text-[11px] text-muted-foreground">
        Bu bo‘lim faqat do‘kon egasi yoki tegishli ruxsatga ega adminlar uchun.
      </p>
    </div>
  );
}

function LoginScreen({
  onLoggedIn,
}: {
  onLoggedIn: (admin: any, csrf: string) => void;
}) {
  const { t } = useLang();
  const [login, setLogin] = useState("owner");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr("");
    setSubmitting(true);
    try {
      const res = await adminFetch("/api/admin/login", {
        method: "POST",
        body: JSON.stringify({ login, password }),
      });
      onLoggedIn(res.admin, res.csrf);
    } catch (error: any) {
      setErr(error.message || "Login yoki parol noto‘g‘ri.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="grain flex min-h-[100dvh] bg-[#f5f2eb] text-[#172641]">
      {/* Left Brand Showcase Panel */}
      <div className="relative hidden w-[49%] flex-col justify-between overflow-hidden bg-[#172641] p-12 text-white lg:flex">
        <div className="pointer-events-none absolute -right-24 -top-24 h-[440px] w-[440px] rounded-full border border-[#c8ac7f]/15" />
        <div className="pointer-events-none absolute -right-8 -top-8 h-[300px] w-[300px] rounded-full border border-[#c8ac7f]/10" />
        <div className="pointer-events-none absolute -bottom-32 -left-24 h-[380px] w-[380px] rounded-full border border-white/[.06]" />

        <div className="relative flex items-center gap-4">
          <img
            src="/whitmore-logo.jpg"
            alt="Withmore"
            onError={(e) => {
              (e.currentTarget as HTMLImageElement).style.display = "none";
            }}
            className="h-14 w-14 rounded-full border border-[#d8c5a6]/50 object-cover shadow-lg"
          />
          <div>
            <div className="font-display text-[17px] font-semibold tracking-[.18em]">
              WITHMORE
            </div>
            <div className="mt-0.5 text-[9px] uppercase tracking-[.24em] text-white/55">
              Classic Menswear
            </div>
          </div>
        </div>

        <div className="relative max-w-md">
          <div className="mb-4 text-[10px] font-bold uppercase tracking-[.24em] text-[#d6bd92]">
            Klassik erkaklar kiyimi · Do‘kon boshqaruvi
          </div>
          <h1 className="font-display text-[44px] font-medium leading-[1.08] tracking-[-.03em]">
            Buyurtmalarni e’tibor bilan boshqaring.
          </h1>
          <p className="mt-4 text-[13px] leading-relaxed text-white/65">
            Yuan kursidan mijoz eshigigacha har bir buyurtmani nazorat qiling.
          </p>
        </div>

        <div className="relative flex items-center justify-between text-[11px] text-white/45">
          <span>Toshkent · O‘zbekiston / Guangzhou · Xitoy</span>
          <LangSwitcher />
        </div>
      </div>

      {/* Right Login Form Panel */}
      <div className="flex flex-1 items-center justify-center p-6 sm:p-12">
        <form onSubmit={submit} className="w-full max-w-[390px] rise-in">
          <div className="mb-8 flex items-center justify-between lg:hidden">
            <div className="flex items-center gap-3.5">
              <img
                src="/whitmore-logo.jpg"
                alt="Withmore"
                onError={(e) => {
                  (e.currentTarget as HTMLImageElement).style.display = "none";
                }}
                className="h-12 w-12 rounded-full border border-[#172641]/20 object-cover"
              />
              <div>
                <div className="font-display text-[16px] font-semibold tracking-[.16em]">
                  WITHMORE
                </div>
                <div className="text-[9px] uppercase tracking-[.22em] text-muted-foreground">
                  {t.adminPanel}
                </div>
              </div>
            </div>
            <LangSwitcher />
          </div>

          <div className="text-[10px] font-bold uppercase tracking-[.22em] text-[#aa8a5e]">
            Xush kelibsiz · Withmore
          </div>
          <h2 className="mt-2 font-display text-[32px] font-medium tracking-[-.03em]">
            Do‘koningiz ishonchli qo‘llarda.
          </h2>
          <p className="mt-1.5 text-[12px] text-muted-foreground">
            Davom etish uchun hisobingizga kiring ({t.loginTitle}).
          </p>

          <div className="mt-7 space-y-4">
            <div>
              <label
                htmlFor="login-username"
                className="mb-1.5 block text-[11px] font-semibold text-[#4d5361]"
              >
                {t.loginLabel}
              </label>
              <input
                id="login-username"
                type="text"
                autoComplete="username"
                required
                value={login}
                onChange={(e) => setLogin(e.target.value)}
                className="h-11 w-full rounded-xl border border-[#ddd6c7] bg-white px-3.5 text-[13px] outline-none transition focus:border-[#172641] focus:ring-2 focus:ring-[#172641]/10"
              />
            </div>

            <div>
              <label
                htmlFor="login-password"
                className="mb-1.5 block text-[11px] font-semibold text-[#4d5361]"
              >
                {t.passwordLabel}
              </label>
              <input
                id="login-password"
                type="password"
                autoComplete="current-password"
                required
                minLength={10}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="h-11 w-full rounded-xl border border-[#ddd6c7] bg-white px-3.5 text-[13px] outline-none transition focus:border-[#172641] focus:ring-2 focus:ring-[#172641]/10"
              />
            </div>

            {err && (
              <div
                role="alert"
                className="rounded-xl border border-[#efc4bc] bg-[#fff3f0] px-3.5 py-2.5 text-[11px] font-semibold text-[#a43b2e]"
              >
                {err}
              </div>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-[#172641] text-[12px] font-bold text-[#f5f1e8] transition hover:bg-[#22345a] disabled:opacity-50 cursor-pointer border-0"
            >
              {submitting ? "Tekshirilmoqda…" : `${t.signIn} →`}
            </button>
          </div>

          <div className="mt-7 rounded-xl border border-[#e5dfd2] bg-[#faf7f0] p-3.5 text-[11px] leading-relaxed text-muted-foreground">
            <span className="font-bold text-[#172641]">
              Maxfiy ish maydoni.
            </span>{" "}
            Har bir kirish va o‘zgarish jamoa faoliyati jurnalida qayd etiladi.
          </div>
        </form>
      </div>
    </div>
  );
}
