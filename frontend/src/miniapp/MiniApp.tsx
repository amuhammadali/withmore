import React, { useEffect, useState } from "react";
import {
  Link,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
  useSearchParams,
} from "react-router-dom";
import { getShopToken, setShopToken, shopFetch } from "../api";
import { formatPrice, useLang } from "../i18n";
import { EmptyState, SkeletonList, StatusBadge, useToast } from "../ui";

declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        initData?: string;
        initDataUnsafe?: any;
        ready?: () => void;
        expand?: () => void;
        BackButton?: {
          show: () => void;
          hide: () => void;
          onClick: (cb: () => void) => void;
          offClick: (cb: () => void) => void;
        };
        openTelegramLink?: (url: string) => void;
      };
    };
  }
}

function ProductImage({
  src,
  alt,
  className = "",
}: {
  src?: string;
  alt: string;
  className?: string;
}) {
  const [failed, setFailed] = useState(false);
  useEffect(() => setFailed(false), [src]);

  if (!src || failed) {
    return (
      <div
        aria-label={`${alt} — rasm yo‘q`}
        className={`flex items-center justify-center bg-[radial-gradient(ellipse_at_50%_35%,#f4eee2_0,#e2d6c1_70%)] ${className}`}
      >
        <div className="text-center p-3">
          <img
            src="/whitmore-logo.jpg"
            alt=""
            onError={(e) => {
              (e.currentTarget as HTMLImageElement).style.display = "none";
            }}
            className="mx-auto h-10 w-10 rounded-full opacity-50 mix-blend-multiply object-cover"
          />
          <div className="mt-2 text-[9px] font-bold uppercase tracking-[.22em] text-[#8a6c43]">
            WHITMORE
          </div>
        </div>
      </div>
    );
  }

  return (
    <img
      src={`/uploads/${src}`}
      alt={alt}
      loading="lazy"
      onError={() => setFailed(true)}
      className={`object-cover ${className}`}
    />
  );
}

export function MiniAppRoot() {
  const { lang, setLang, t } = useLang();
  const { toast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();

  const [ready, setReady] = useState(false);
  const [customer, setCustomer] = useState<any>(null);
  const [content, setContent] = useState<any>(null);
  const [categories, setCategories] = useState<any[]>([]);
  const [cart, setCart] = useState<{ items: any[]; total: number }>({
    items: [],
    total: 0,
  });
  const [favIds, setFavIds] = useState<number[]>([]);

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    tg?.ready?.();
    tg?.expand?.();
  }, []);

  useEffect(() => {
    const bb = window.Telegram?.WebApp?.BackButton;
    if (!bb) return;
    const isHome =
      location.pathname === "/miniapp" || location.pathname === "/miniapp/";
    const handler = () => navigate(-1);
    if (isHome) {
      bb.hide();
    } else {
      bb.show();
      bb.onClick(handler);
    }
    return () => {
      bb.offClick?.(handler);
    };
  }, [location.pathname, navigate]);

  useEffect(() => {
    async function boot() {
      try {
        const tgInit = window.Telegram?.WebApp?.initData || "";
        const source = searchParams.get("utm_source") || "";
        const medium = searchParams.get("utm_medium") || "";
        const campaign = searchParams.get("utm_campaign") || "";
        const startParam =
          window.Telegram?.WebApp?.initDataUnsafe?.start_param ||
          searchParams.get("start") ||
          "";

        if (startParam.startsWith("prod_")) {
          const parts = startParam.split("_");
          const pid = Number(parts[1]);
          if (pid > 0 && !location.pathname.includes(`/product/${pid}`)) {
            navigate(`/miniapp/product/${pid}`, { replace: true });
          }
        }

        let c = null;
        if (getShopToken() && !tgInit && !source) {
          try {
            c = await shopFetch("/api/shop/me");
          } catch {
            c = null;
          }
        }
        if (!c) {
          const authRes = await shopFetch("/api/shop/auth", {
            method: "POST",
            body: JSON.stringify({
              init_data: tgInit,
              source,
              medium,
              campaign,
              start_param: startParam,
            }),
          });
          setShopToken(authRes.token);
          c = authRes.customer;
          if (c?.language === "ru" || c?.language === "uz") {
            setLang(c.language);
          }
        }
        setCustomer(c);
        const [cnt, cats, crt, favs] = await Promise.all([
          shopFetch("/api/shop/content"),
          shopFetch("/api/shop/categories"),
          shopFetch("/api/shop/cart"),
          shopFetch("/api/shop/favorites"),
        ]);
        setContent(cnt);
        setCategories(cats);
        setCart(crt);
        setFavIds(favs.ids || []);
      } catch (e: any) {
        toast(e.message || t.errorToast, "error");
      } finally {
        setReady(true);
      }
    }
    boot();
  }, []);

  const trackEvent = (type: string, product_id?: number) => {
    shopFetch("/api/shop/events", {
      method: "POST",
      body: JSON.stringify({ type, product_id: product_id || null }),
    }).catch(() => {});
  };

  const toggleFavorite = async (pid: number) => {
    try {
      const r = await shopFetch(`/api/shop/favorites/${pid}`, {
        method: "POST",
      });
      setFavIds((prev) =>
        r.favorite ? [...prev, pid] : prev.filter((id) => id !== pid)
      );
    } catch (e: any) {
      toast(e.message, "error");
    }
  };

  const updateCart = async (items: { variant_id: number; qty: number }[]) => {
    const updated = await shopFetch("/api/shop/cart", {
      method: "PUT",
      body: JSON.stringify({ items }),
    });
    setCart(updated);
    return updated;
  };

  const addToCart = async (variant_id: number, product_id: number, qty = 1) => {
    try {
      const existing = cart.items.map((i) => ({
        variant_id: i.variant_id,
        qty: i.qty,
      }));
      const found = existing.find((x) => x.variant_id === variant_id);
      if (found) found.qty += qty;
      else existing.push({ variant_id, qty });
      await updateCart(existing);
      trackEvent("add_to_cart", product_id);
      toast(t.addedToCart);
    } catch (e: any) {
      toast(e.message, "error");
    }
  };

  const cartCount = cart.items.reduce((s, i) => s + i.qty, 0);
  const isHome =
    location.pathname === "/miniapp" || location.pathname === "/miniapp/";

  return (
    <div className="grain min-h-[100dvh] flex flex-col bg-[#f4efe5] text-[#172641] pb-20">
      {/* Replit Editorial Header */}
      <header className="sticky top-0 z-30 shrink-0 border-b border-[#172641]/10 bg-[#f4efe5]/92 backdrop-blur-xl">
        <div className="mx-auto flex min-h-14 w-full max-w-[1160px] items-center justify-between gap-2 px-4 sm:px-6">
          {isHome ? (
            <Link
              to="/miniapp"
              className="flex items-center gap-2.5 no-underline text-[#172641]"
            >
              <img
                src="/whitmore-logo.jpg"
                alt="Whitmore"
                onError={(e) => {
                  (e.currentTarget as HTMLImageElement).style.display = "none";
                }}
                className="h-8 w-8 rounded-full object-cover border border-[#172641]/20"
              />
              <span className="font-display text-[15px] font-semibold tracking-[.22em]">
                WHITMORE
              </span>
            </Link>
          ) : (
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="flex items-center gap-1.5 text-[12px] font-semibold text-[#172641] bg-transparent border-0 cursor-pointer py-2 px-1"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M15 18l-6-6 6-6" />
              </svg>
              <span>
                {location.pathname.startsWith("/miniapp/product/")
                  ? t.catalog
                  : t.home}
              </span>
            </button>
          )}

          <div className="flex items-center gap-2">
            {/* Pill Language Switcher */}
            <div
              className="flex rounded-full border border-[#172641]/15 p-0.5 text-[10px] font-bold bg-[#fbf8f2]"
              role="group"
              aria-label="Til"
            >
              {(["uz", "ru"] as const).map((l) => (
                <button
                  key={l}
                  type="button"
                  onClick={() => setLang(l)}
                  className={`rounded-full px-2.5 py-1 uppercase transition cursor-pointer border-0 ${
                    lang === l
                      ? "bg-[#172641] text-[#f4efe5]"
                      : "bg-transparent text-[#172641]/60"
                  }`}
                >
                  {l}
                </button>
              ))}
            </div>

            {/* Cart Button */}
            <Link
              to="/miniapp/cart"
              aria-label={t.cart}
              className="relative rounded-full p-2.5 text-[#172641] transition active:scale-95 no-underline"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.7"
              >
                <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z" />
                <line x1="3" y1="6" x2="21" y2="6" />
                <path d="M16 10a4 4 0 0 1-8 0" />
              </svg>
              {cartCount > 0 && (
                <span className="absolute right-0.5 top-0.5 flex h-[18px] min-w-[18px] items-center justify-center rounded-full bg-[#a8865a] px-1 text-[10px] font-bold text-white">
                  {cartCount}
                </span>
              )}
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content Container */}
      <main className="mx-auto w-full max-w-[1160px] flex-1 pb-6">
        {!ready ? (
          <div className="p-4">
            <SkeletonList count={6} />
          </div>
        ) : (
          <Routes>
            <Route
              index
              element={
                <HomeScreen
                  content={content}
                  categories={categories}
                  customerName={customer?.name}
                  favIds={favIds}
                  onToggleFav={toggleFavorite}
                />
              }
            />
            <Route
              path="catalog"
              element={
                <CatalogScreen
                  categories={categories}
                  favIds={favIds}
                  onToggleFav={toggleFavorite}
                />
              }
            />
            <Route
              path="product/:id"
              element={
                <ProductScreen
                  content={content}
                  favIds={favIds}
                  onToggleFav={toggleFavorite}
                  onAddToCart={addToCart}
                  onView={(pid) => trackEvent("product_view", pid)}
                />
              }
            />
            <Route
              path="cart"
              element={
                <CartScreen
                  cart={cart}
                  onUpdateCart={updateCart}
                  onCheckoutClick={() => trackEvent("checkout_click")}
                />
              }
            />
            <Route
              path="checkout"
              element={
                <CheckoutScreen
                  cart={cart}
                  customer={customer}
                  content={content}
                  onOrderCreated={(newOrder) => {
                    setCart({ items: [], total: 0 });
                    navigate(`/miniapp/order/${newOrder.code}`, {
                      state: { order: newOrder },
                    });
                  }}
                />
              }
            />
            <Route
              path="orders"
              element={<OrdersScreen content={content} />}
            />
            <Route
              path="order/:code"
              element={
                <OrderResultScreen
                  content={content}
                  onContactClick={() => trackEvent("contact_click")}
                />
              }
            />
            <Route
              path="about"
              element={
                <AboutScreen
                  content={content}
                  lang={lang}
                  favIds={favIds}
                  onToggleFav={toggleFavorite}
                />
              }
            />
          </Routes>
        )}
      </main>

      {/* Floating Creative Capsule Bottom Navigation Bar */}
      <nav
        aria-label="Do‘kon bo‘limlari"
        className="fixed bottom-3 left-0 right-0 z-30 px-2.5 sm:bottom-4 sm:px-5 pointer-events-none"
      >
        <div className="pointer-events-auto mx-auto grid max-w-[600px] grid-cols-5 items-center gap-1 rounded-full border border-[#d6bd92]/35 bg-[#172641]/95 p-1.5 text-[#f4efe5] shadow-[0_18px_42px_-8px_rgba(14,24,42,0.55),0_0_0_1px_rgba(255,255,255,0.07)_inset] backdrop-blur-xl">
          <NavTab to="/miniapp" exact label={t.home} icon="home" />
          <NavTab
            to="/miniapp/catalog"
            label={t.catalog}
            alsoMatch="/miniapp/product"
            icon="catalog"
          />
          <NavTab
            to="/miniapp/cart"
            label={t.cart}
            badge={cartCount > 0 ? cartCount : undefined}
            icon="cart"
          />
          <NavTab
            to="/miniapp/orders"
            label={lang === "ru" ? "Заказы" : "Buyurtmalar"}
            alsoMatch="/miniapp/order/"
            icon="orders"
          />
          <NavTab
            to="/miniapp/about"
            label={lang === "ru" ? "О нас" : "Haqimizda"}
            icon="about"
          />
        </div>
      </nav>
    </div>
  );
}

function NavTab({
  to,
  label,
  exact,
  alsoMatch,
  badge,
  icon,
}: {
  to: string;
  label: string;
  exact?: boolean;
  alsoMatch?: string;
  badge?: number;
  icon: "home" | "catalog" | "cart" | "orders" | "about";
}) {
  const { pathname } = useLocation();
  const active = exact
    ? pathname === to || pathname === to + "/"
    : pathname.startsWith(to) || (alsoMatch ? pathname.startsWith(alsoMatch) : false);

  return (
    <Link
      to={to}
      className={`group relative flex min-h-[50px] min-w-0 flex-col items-center justify-center gap-1 rounded-full px-1.5 py-1.5 no-underline transition-all duration-300 active:scale-95 ${
        active
          ? "bg-gradient-to-b from-[#ebdcc0] to-[#cfa972] text-[#172641] shadow-[0_6px_18px_-3px_rgba(214,189,146,0.45)]"
          : "text-[#f4efe5]/70 hover:bg-white/10 hover:text-[#f4efe5]"
      }`}
    >
      <div className="relative flex items-center justify-center">
        {icon === "home" && (
          <svg
            width="17"
            height="17"
            viewBox="0 0 24 24"
            fill={active ? "currentColor" : "none"}
            stroke="currentColor"
            strokeWidth={active ? "2" : "1.75"}
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M3 10.5L12 3l9 7.5V20a1 1 0 0 1-1 1h-5.5v-6h-5v6H4a1 1 0 0 1-1-1v-9.5z" />
          </svg>
        )}
        {icon === "catalog" && (
          <svg
            width="17"
            height="17"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={active ? "2.1" : "1.75"}
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <rect x="3" y="3" width="7" height="7" rx="2" />
            <rect x="14" y="3" width="7" height="7" rx="2" />
            <rect x="14" y="14" width="7" height="7" rx="2" />
            <rect x="3" y="14" width="7" height="7" rx="2" />
          </svg>
        )}
        {icon === "cart" && (
          <svg
            width="17"
            height="17"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={active ? "2.1" : "1.75"}
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z" />
            <line x1="3" y1="6" x2="21" y2="6" />
            <path d="M16 10a4 4 0 0 1-8 0" />
          </svg>
        )}
        {icon === "orders" && (
          <svg
            width="17"
            height="17"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={active ? "2.1" : "1.75"}
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z" />
            <path d="m3.3 7 8.7 5 8.7-5" />
            <path d="M12 22V12" />
          </svg>
        )}
        {icon === "about" && (
          <svg
            width="17"
            height="17"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={active ? "2.1" : "1.75"}
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" />
          </svg>
        )}
        {badge !== undefined && (
          <span
            className={` -right-2.5 -top-1.5 absolute flex h-4 min-w-[16px] items-center justify-center rounded-full px-1 text-[9px] font-extrabold leading-none shadow-sm ${
              active
                ? "bg-[#172641] text-[#f4efe5]"
                : "bg-[#d6bd92] text-[#172641]"
            }`}
          >
            {badge}
          </span>
        )}
      </div>
      <span
        className={`max-w-full truncate text-[9px] uppercase tracking-[.08em] sm:text-[10px] sm:tracking-[.12em] ${
          active ? "font-extrabold" : "font-semibold"
        }`}
      >
        {label}
      </span>
    </Link>
  );
}

// ---------------- REPLIT EDITORIAL PRODUCT CARD ----------------
function getCategoryIcon(name: string): string {
  const n = (name || "").toLowerCase();
  if (n.includes("kostyum") || n.includes("smoking") || n.includes("костюм") || n.includes("пиджак")) return "👔";
  if (n.includes("ko'ylak") || n.includes("koylak") || n.includes("rubashka") || n.includes("рубашк")) return "👔";
  if (n.includes("poyabzal") || n.includes("tufli") || n.includes("oyoq") || n.includes("обув") || n.includes("туфли") || n.includes("krossovk")) return "👞";
  if (n.includes("shim") || n.includes("bryuk") || n.includes("брюк") || n.includes("джинс")) return "👖";
  if (n.includes("kurtka") || n.includes("palto") || n.includes("nimcha") || n.includes("куртк") || n.includes("пальто")) return "🧥";
  if (n.includes("aksessuar") || n.includes("galstuk") || n.includes("kamar") || n.includes("аксессуар")) return "🎒";
  return "✨";
}

function ProductCard({
  p,
  isFav,
  onToggleFav,
}: {
  p: any;
  isFav: boolean;
  onToggleFav: (id: number) => void;
}) {
  const { lang, t } = useLang();
  const name = lang === "ru" ? p.name_ru || p.name_uz : p.name_uz;
  const isStock = p.sale_type === "stock";

  return (
    <div className="group relative min-w-0 self-start rise-in rounded-2xl border border-[#172641]/10 bg-white p-2.5 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-[#172641]/35 hover:shadow-xl">
      <Link
        to={`/miniapp/product/${p.id}`}
        className="block w-full min-w-0 text-left no-underline text-[#172641]"
      >
        <div className="relative aspect-[3/4] overflow-hidden rounded-xl bg-[#e6dccb]">
          <ProductImage
            src={p.thumb}
            alt={name}
            className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105"
          />

          {/* Top-left Sale Type Badge */}
          <span className={`absolute left-2 top-2 rounded-full backdrop-blur-md px-2.5 py-1 text-[9px] font-extrabold uppercase tracking-[.14em] shadow-xs border ${
            isStock
              ? "bg-[#1b4332]/85 text-[#e8f5e9] border-[#74c69d]/40"
              : "bg-[#172641]/85 text-[#faf7f2] border-[#c5a676]/40"
          }`}>
            {isStock ? t.inStockBadge : t.preorderBadge}
          </span>

          {/* Sold out bottom bar */}
          {p.sold_out && (
            <span className="absolute inset-x-0 bottom-0 bg-[#172641]/90 py-1.5 text-center text-[9px] font-bold uppercase tracking-[.16em] text-white backdrop-blur-xs">
              {t.soldOut}
            </span>
          )}
        </div>

        <div className="mt-2.5 px-1">
          <div className="line-clamp-2 font-display text-[15px] font-semibold leading-snug text-[#172641] group-hover:text-[#8a6c43] transition-colors">
            {name}
          </div>
          <div className="mt-2 flex items-center justify-between gap-1">
            <span className="text-[13px] font-bold text-[#8a6c43]">
              {formatPrice(p.price)}
            </span>
            <span className="inline-flex items-center gap-1 rounded-full border border-[#dccab0] bg-[#faf7f2] px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-[#172641] transition-all duration-200 group-hover:bg-[#172641] group-hover:text-[#f4efe5] group-hover:border-[#172641] group-hover:shadow-[0_2px_8px_rgba(23,38,65,0.2)]">
              Tanlash →
            </span>
          </div>
        </div>
      </Link>

      {/* Top-right Favorite Heart Button */}
      <button
        type="button"
        aria-label={t.favorites}
        onClick={(e) => {
          e.stopPropagation();
          onToggleFav(p.id);
        }}
        className="absolute right-3.5 top-3.5 flex h-8 w-8 items-center justify-center rounded-full backdrop-blur-md bg-white/90 text-[#172641] transition-all duration-200 active:scale-90 cursor-pointer border border-[#dccab0]/60 shadow-[0_2px_8px_rgba(0,0,0,0.08)] hover:bg-white hover:scale-110 hover:shadow-[0_4px_12px_rgba(163,70,60,0.2)]"
      >
        <svg
          width="15"
          height="15"
          viewBox="0 0 24 24"
          fill={isFav ? "#a3463c" : "none"}
          stroke={isFav ? "#a3463c" : "currentColor"}
          strokeWidth="1.8"
        >
          <path d="M12 21s-7-4.5-9.5-9A5.5 5.5 0 0 1 12 6a5.5 5.5 0 0 1 9.5 6c-2.5 4.5-9.5 9-9.5 9z" />
        </svg>
      </button>
    </div>
  );
}

// ---------------- HOME SCREEN (REPLIT EDITORIAL) ----------------
function HomeScreen({
  content,
  categories,
  customerName,
  favIds,
  onToggleFav,
}: {
  content: any;
  categories: any[];
  customerName?: string;
  favIds: number[];
  onToggleFav: (id: number) => void;
}) {
  const { lang, t } = useLang();
  const [featured, setFeatured] = useState<any[]>([]);
  const [allProds, setAllProds] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      shopFetch("/api/shop/products?featured=true"),
      shopFetch("/api/shop/products"),
    ])
      .then(([feat, all]) => {
        setFeatured(feat);
        setAllProds(all);
      })
      .finally(() => setLoading(false));
  }, []);

  const heroTitle =
    lang === "ru" ? content?.hero_title_ru : content?.hero_title_uz;
  const heroText =
    lang === "ru" ? content?.hero_text_ru : content?.hero_text_uz;
  const displayProds = (featured.length > 0 ? featured : allProds).slice(0, 6);

  return (
    <div className="rise-in">
      {/* Replit Deep Navy Editorial Hero */}
      <section className="relative overflow-hidden bg-[#172641] text-[#f4efe5]">
        {content?.hero_image ? (
          <img
            src={`/uploads/${content.hero_image}`}
            alt=""
            className="absolute inset-0 h-full w-full object-cover opacity-55"
          />
        ) : (
          <>
            <div className="pointer-events-none absolute -right-24 -top-10 h-80 w-80 rounded-full border border-[#d6bd92]/25" />
            <div className="pointer-events-none absolute -right-8 top-6 h-56 w-56 rounded-full border border-[#d6bd92]/15" />
          </>
        )}
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-[#172641] via-[#172641]/40 to-transparent" />

        <div className="relative flex min-h-[320px] flex-col justify-end px-5 pb-8 pt-16 sm:min-h-[380px] sm:px-8 lg:px-12 lg:pb-12">
          {customerName && !customerName.startsWith("#") ? (
            <div className="mb-3 text-[10px] font-semibold uppercase tracking-[.22em] text-[#d6bd92]">
              Xush kelibsiz, {customerName}
            </div>
          ) : (
            <div className="mb-3 text-[10px] font-semibold uppercase tracking-[.22em] text-[#d6bd92]">
              WHITMORE · CLASSIC MENSWEAR
            </div>
          )}
          <h1 className="max-w-3xl font-display text-[clamp(2rem,5vw,3.5rem)] font-medium leading-[1.06] tracking-[-.02em] text-[#f4efe5]">
            {heroTitle || t.brandSub}
          </h1>
          {heroText && (
            <p className="mt-3 max-w-md text-[13px] leading-6 text-[#f4efe5]/75">
              {heroText}
            </p>
          )}
          <div className="mt-7 flex flex-wrap gap-3">
            <Link
              to="/miniapp/catalog"
              className="inline-flex items-center gap-2 bg-[#d6bd92] px-6 py-3.5 text-[11px] font-bold uppercase tracking-[.18em] text-[#172641] no-underline transition active:scale-[.98]"
            >
              <span>{t.catalog}</span>
              <span>→</span>
            </Link>
            <Link
              to="/miniapp/about"
              className="inline-flex items-center gap-2 border border-[#f4efe5]/30 px-5 py-3.5 text-[11px] font-bold uppercase tracking-[.16em] text-[#f4efe5] no-underline transition hover:bg-white/10"
            >
              {t.about}
            </Link>
          </div>
        </div>
      </section>

      {/* Editorial Luxury Category Chips Row */}
      {categories.length > 0 && (
        <section
          aria-label="Kategoriyalar"
          className="px-4 py-4"
        >
          <div className="flex items-center justify-between mb-2.5">
            <span className="text-[10px] font-bold uppercase tracking-[.2em] text-[#8a6c43]">
              {lang === "ru" ? "Коллекции и категории" : "Kolleksiyalar va bo‘limlar"}
            </span>
            <Link
              to="/miniapp/catalog"
              className="text-[11px] font-semibold text-[#172641] hover:underline"
            >
              {lang === "ru" ? "Весь каталог →" : "Barchasi →"}
            </Link>
          </div>
          <div className="flex gap-2.5 overflow-x-auto no-scrollbar pb-1">
            <Link
              to="/miniapp/catalog"
              className="shrink-0 flex items-center gap-2 rounded-2xl bg-gradient-to-r from-[#172641] via-[#223558] to-[#121c2e] px-4 py-2.5 text-[11px] font-bold text-[#faf7f2] shadow-[0_4px_16px_rgba(23,38,65,0.28)] ring-2 ring-[#c5a676] ring-offset-2 ring-offset-[#f6f2ea] no-underline transition-all duration-200 hover:scale-[1.02] active:scale-95"
            >
              <span className="text-sm drop-shadow-sm">✨</span>
              <span className="tracking-wide">{t.allCategories}</span>
            </Link>
            {categories.map((c) => {
              const label = lang === "ru" ? c.name_ru || c.name_uz : c.name_uz;
              const icon = getCategoryIcon(label);
              return (
                <Link
                  key={c.id}
                  to={`/miniapp/catalog?category=${c.id}`}
                  className="shrink-0 flex items-center gap-2 rounded-2xl border border-[#dccab0] bg-gradient-to-b from-white to-[#fbf7f0] px-4 py-2.5 text-[11px] font-bold text-[#172641] shadow-[0_2px_8px_rgba(23,38,65,0.04)] no-underline transition-all duration-200 hover:border-[#c5a676] hover:shadow-[0_6px_20px_rgba(197,166,118,0.28)] hover:-translate-y-0.5 hover:text-[#0b1728] active:scale-95"
                >
                  <span className="text-sm">{icon}</span>
                  <span className="tracking-wide">{label}</span>
                </Link>
              );
            })}
          </div>
        </section>
      )}

      {/* Featured / Collection Grid */}
      <section className="px-4 pt-2">
        <div className="mb-4 flex items-end justify-between border-b border-[#172641]/15 pb-2.5">
          <h2 className="font-display text-[24px] font-medium text-[#172641]">
            {featured.length > 0 ? t.featured : t.catalog}
          </h2>
          <Link
            to="/miniapp/catalog"
            className="text-[10px] font-bold uppercase tracking-[.16em] text-[#8a6c43] no-underline hover:underline"
          >
            {t.viewAll} · {allProds.length}
          </Link>
        </div>

        {loading ? (
          <SkeletonList count={4} />
        ) : displayProds.length === 0 ? (
          <EmptyState text={t.emptyCatalog} />
        ) : (
          <div className="miniapp-product-grid">
            {displayProds.map((p) => (
              <ProductCard
                key={p.id}
                p={p}
                isFav={favIds.includes(p.id)}
                onToggleFav={onToggleFav}
              />
            ))}
          </div>
        )}
      </section>

      {/* Editorial Footer Note */}
      <section className="mx-4 mt-10 border-t border-[#172641]/15 pt-6">
        <div className="text-[9px] font-bold uppercase tracking-[.22em] text-[#8a6c43]">
          Whitmore uslubi
        </div>
        <p className="mt-2 font-display text-[20px] leading-snug text-[#172641]">
          Sokin klassika. Aniq bichim. Har kuni kiyiladigan ishonch.
        </p>
        <Link
          to="/miniapp/about"
          className="mt-4 inline-block text-[11px] font-semibold text-[#172641] underline underline-offset-4"
        >
          {t.deliveryAndReturnTerms}
        </Link>
      </section>
    </div>
  );
}

// ---------------- CATALOG SCREEN ----------------
function CatalogScreen({
  categories,
  favIds,
  onToggleFav,
}: {
  categories: any[];
  favIds: number[];
  onToggleFav: (id: number) => void;
}) {
  const { lang, t } = useLang();
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedCat = Number(searchParams.get("category") || 0);
  const [q, setQ] = useState("");
  const [sortBy, setSortBy] = useState("featured");
  const [saleType, setSaleType] = useState("all");
  const [onlyFavs, setOnlyFavs] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (selectedCat) params.set("category_id", String(selectedCat));
    if (q.trim()) params.set("q", q.trim());
    shopFetch(`/api/shop/products?${params.toString()}`)
      .then((res) => setItems(res))
      .finally(() => setLoading(false));
  }, [selectedCat, q]);

  const filtered = items
    .filter((p) => {
      if (saleType !== "all" && p.sale_type !== saleType) return false;
      if (onlyFavs && !favIds.includes(p.id)) return false;
      return true;
    })
    .sort((a, b) => {
      if (sortBy === "priceAsc") return a.price - b.price;
      if (sortBy === "priceDesc") return b.price - a.price;
      return Number(b.featured) - Number(a.featured);
    });

  return (
    <div className="px-4 pt-5 rise-in">
      <h1 className="font-display text-[30px] leading-none text-[#172641]">
        {t.catalog}
      </h1>

      {/* Search & Filter Controls */}
      <div className="mt-4 flex items-center gap-2">
        <label className="relative flex-1">
          <span className="sr-only">{t.search}</span>
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[#c5a676] pointer-events-none transition-colors"
          >
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            type="search"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder={t.searchPlaceholder}
            className="h-11 w-full rounded-2xl border border-[#dccab0] bg-white/95 pl-10 pr-4 text-[13px] text-[#172641] placeholder-[#172641]/40 shadow-[0_2px_8px_rgba(23,38,65,0.03)] outline-none transition-all duration-200 focus:border-[#c5a676] focus:ring-2 focus:ring-[#c5a676]/30 focus:shadow-[0_4px_16px_rgba(197,166,118,0.18)]"
          />
        </label>

        <button
          type="button"
          onClick={() => setShowFilters((v) => !v)}
          aria-label="Filtrlar"
          className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl border transition-all duration-200 cursor-pointer active:scale-95 ${
            showFilters
              ? "border-[#c5a676] bg-gradient-to-r from-[#172641] to-[#223558] text-[#faf7f2] shadow-[0_4px_14px_rgba(23,38,65,0.3)] ring-2 ring-[#c5a676]/50"
              : "border-[#dccab0] bg-white/95 text-[#172641] shadow-[0_2px_8px_rgba(23,38,65,0.03)] hover:border-[#c5a676] hover:bg-white hover:text-[#0b1728] hover:shadow-[0_4px_16px_rgba(197,166,118,0.22)] hover:-translate-y-0.5"
          }`}
        >
          <svg
            width="17"
            height="17"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.9"
          >
            <line x1="4" y1="6" x2="20" y2="6" />
            <line x1="7" y1="12" x2="17" y2="12" />
            <line x1="10" y1="18" x2="14" y2="18" />
          </svg>
        </button>

        <button
          type="button"
          onClick={() => setOnlyFavs((v) => !v)}
          className={`flex h-11 shrink-0 items-center gap-1.5 rounded-2xl border px-3 text-[11px] font-bold transition-all duration-200 cursor-pointer active:scale-95 ${
            onlyFavs
              ? "border-[#a3463c] bg-gradient-to-r from-[#8f2d24] to-[#b34033] text-white shadow-[0_4px_14px_rgba(163,70,60,0.35)] ring-2 ring-[#f0a8a0]/60"
              : "border-[#dccab0] bg-white/95 text-[#172641] shadow-[0_2px_8px_rgba(23,38,65,0.03)] hover:border-[#c5a676] hover:bg-white hover:text-[#a3463c] hover:shadow-[0_4px_16px_rgba(163,70,60,0.18)] hover:-translate-y-0.5"
          }`}
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill={onlyFavs ? "currentColor" : "none"}
            stroke="currentColor"
            strokeWidth="1.9"
          >
            <path d="M12 21s-7-4.5-9.5-9A5.5 5.5 0 0 1 12 6a5.5 5.5 0 0 1 9.5 6c-2.5 4.5-9.5 9-9.5 9z" />
          </svg>
          <span className="hidden sm:inline">{t.favorites}</span>
          {favIds.length > 0 && (
            <span className={`text-[10px] px-1.5 py-0.2 rounded-full ${onlyFavs ? "bg-white/25 text-white" : "bg-[#172641]/10 text-[#172641]"}`}>
              {favIds.length}
            </span>
          )}
        </button>
      </div>

      {/* Collapsible Sort & Type Drawer */}
      {showFilters && (
        <div className="rise-in mt-2 grid grid-cols-2 gap-2 rounded-2xl border border-[#dccab0] bg-white/95 p-3.5 shadow-sm">
          <label className="text-[10px] font-semibold uppercase tracking-wider text-[#172641]/70">
            Tartib
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="mt-1.5 h-10 w-full rounded-xl border border-[#dccab0] bg-[#faf7f2] px-2.5 text-[12px] font-medium normal-case tracking-normal text-[#172641] outline-none focus:border-[#c5a676]"
            >
              <option value="featured">Tanlanganlar avval</option>
              <option value="priceAsc">Arzonroq avval</option>
              <option value="priceDesc">Qimmatroq avval</option>
            </select>
          </label>
          <label className="text-[10px] font-semibold uppercase tracking-wider text-[#172641]/70">
            Turi
            <select
              value={saleType}
              onChange={(e) => setSaleType(e.target.value)}
              className="mt-1.5 h-10 w-full rounded-xl border border-[#dccab0] bg-[#faf7f2] px-2.5 text-[12px] font-medium normal-case tracking-normal text-[#172641] outline-none focus:border-[#c5a676]"
            >
              <option value="all">{t.allCategories}</option>
              <option value="stock">{t.inStockBadge}</option>
              <option value="preorder">{t.preorderBadge}</option>
            </select>
          </label>
        </div>
      )}

      {/* Category Pill Strip (Luxury Rounded Interactive Badges) */}
      <div className="no-scrollbar -mx-4 mt-3 flex items-center gap-2 overflow-x-auto px-4 pb-2">
        <button
          type="button"
          onClick={() => setSearchParams({})}
          className={`shrink-0 inline-flex items-center gap-2 rounded-2xl px-4 py-2.5 text-[11px] font-bold tracking-wide transition-all duration-200 cursor-pointer ${
            !selectedCat
              ? "bg-gradient-to-r from-[#172641] via-[#223558] to-[#121c2e] text-[#faf7f2] shadow-[0_4px_16px_rgba(23,38,65,0.28)] ring-2 ring-[#c5a676] ring-offset-2 ring-offset-[#f6f2ea] scale-[1.02]"
              : "border border-[#dccab0] bg-gradient-to-b from-white to-[#fbf7f0] text-[#172641] shadow-[0_2px_8px_rgba(23,38,65,0.04)] hover:border-[#c5a676] hover:shadow-[0_6px_20px_rgba(197,166,118,0.28)] hover:-translate-y-0.5 hover:text-[#0b1728] active:scale-95"
          }`}
        >
          <span className="text-sm drop-shadow-sm">✨</span>
          <span>{t.allCategories}</span>
        </button>
        {categories.map((c) => {
          const active = selectedCat === c.id;
          const label = lang === "ru" ? c.name_ru || c.name_uz : c.name_uz;
          const icon = getCategoryIcon(label);
          return (
            <button
              key={c.id}
              type="button"
              onClick={() => setSearchParams({ category: String(c.id) })}
              className={`shrink-0 inline-flex items-center gap-2 rounded-2xl px-4 py-2.5 text-[11px] font-bold tracking-wide transition-all duration-200 cursor-pointer ${
                active
                  ? "bg-gradient-to-r from-[#172641] via-[#223558] to-[#121c2e] text-[#faf7f2] shadow-[0_4px_16px_rgba(23,38,65,0.28)] ring-2 ring-[#c5a676] ring-offset-2 ring-offset-[#f6f2ea] scale-[1.02]"
                  : "border border-[#dccab0] bg-gradient-to-b from-white to-[#fbf7f0] text-[#172641] shadow-[0_2px_8px_rgba(23,38,65,0.04)] hover:border-[#c5a676] hover:shadow-[0_6px_20px_rgba(197,166,118,0.28)] hover:-translate-y-0.5 hover:text-[#0b1728] active:scale-95"
              }`}
            >
              <span className="text-sm transition-transform duration-200 group-hover:scale-110">{icon}</span>
              <span>{label}</span>
            </button>
          );
        })}
      </div>

      <div className="mb-4 mt-2.5 text-[10px] font-semibold uppercase tracking-[.16em] text-[#172641]/55">
        {filtered.length} ta mahsulot
      </div>

      {loading ? (
        <SkeletonList count={6} />
      ) : filtered.length === 0 ? (
        <EmptyState text={t.emptyCatalog} />
      ) : (
        <div className="miniapp-product-grid">
          {filtered.map((p) => (
            <ProductCard
              key={p.id}
              p={p}
              isFav={favIds.includes(p.id)}
              onToggleFav={onToggleFav}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ---------------- PRODUCT DETAIL SCREEN ----------------
function ProductScreen({
  content,
  favIds,
  onToggleFav,
  onAddToCart,
  onView,
}: {
  content: any;
  favIds: number[];
  onToggleFav: (id: number) => void;
  onAddToCart: (variantId: number, productId: number, qty?: number) => void;
  onView: (pid: number) => void;
}) {
  const { id } = useParams();
  const navigate = useNavigate();
  const { lang, t } = useLang();
  const { toast } = useToast();
  const [product, setProduct] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [imgIdx, setImgIdx] = useState(0);
  const [touchStartX, setTouchStartX] = useState<number | null>(null);
  const [selectedVariantId, setSelectedVariantId] = useState<number | null>(
    null
  );
  const [qty, setQty] = useState(1);
  const [showChart, setShowChart] = useState(false);
  const [showSizeCalc, setShowSizeCalc] = useState(false);
  const [heightCm, setHeightCm] = useState("176");
  const [weightKg, setWeightKg] = useState("75");
  const [fitPref, setFitPref] = useState<"regular" | "relaxed">("regular");
  const [showQuickModal, setShowQuickModal] = useState(false);
  const [quickName, setQuickName] = useState("");
  const [quickPhone, setQuickPhone] = useState("+998");
  const [quickCity, setQuickCity] = useState("Toshkent");
  const [quickLoading, setQuickLoading] = useState(false);
  const [reviews, setReviews] = useState<any[]>([]);
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [revName, setRevName] = useState("");
  const [revCity, setRevCity] = useState("Samarqand");
  const [revText, setRevText] = useState("");
  const [revSubmitting, setRevSubmitting] = useState(false);

  useEffect(() => {
    shopFetch("/api/shop/reviews")
      .then((res) => setReviews(Array.isArray(res) ? res : []))
      .catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    setImgIdx(0);
    setQty(1);
    shopFetch(`/api/shop/products/${id}`)
      .then((res) => {
        setProduct(res);
        const firstAvail = (res.variants || []).find((v: any) => v.available);
        setSelectedVariantId(firstAvail ? firstAvail.id : null);
        onView(res.id);
      })
      .catch((e) => toast(e.message, "error"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="p-4">
        <SkeletonList count={2} />
      </div>
    );
  }
  if (!product) {
    return (
      <div className="p-4">
        <EmptyState text={t.emptyCatalog} />
      </div>
    );
  }

  const name =
    lang === "ru" ? product.name_ru || product.name_uz : product.name_uz;
  const desc =
    lang === "ru" ? product.desc_ru || product.desc_uz : product.desc_uz;
  const images: string[] = product.images || [];
  const availableVariants = (product.variants || []).filter(
    (v: any) => v.available
  );
  const soldOutVariants = (product.variants || []).filter(
    (v: any) => !v.available
  );
  const selectedVariant = (product.variants || []).find(
    (v: any) => v.id === selectedVariantId
  );

  // Compute recommended size based on height (cm), weight (kg), and fit preference
  const calcRecommendation = () => {
    const h = Number(heightCm) || 176;
    const w = Number(weightKg) || 75;
    const adjW = fitPref === "relaxed" ? w + 5 : w;
    let letter = "L";
    let numeric = "50";
    if (adjW < 64 && h < 174) {
      letter = "S";
      numeric = "46";
    } else if (adjW < 73 && h < 179) {
      letter = "M";
      numeric = "48";
    } else if (adjW < 83 && h < 185) {
      letter = "L";
      numeric = "50";
    } else if (adjW < 93 && h < 190) {
      letter = "XL";
      numeric = "52";
    } else if (adjW < 104) {
      letter = "XXL";
      numeric = "54";
    } else {
      letter = "3XL";
      numeric = "56";
    }
    const matchingVariant = availableVariants.find((v: any) => {
      const s = String(v.size || "").trim().toUpperCase();
      return s === letter || s === numeric || (letter === "XXL" && s === "2XL");
    });
    return { letter, numeric, matchingVariant };
  };
  const rec = calcRecommendation();

  const subscribeRestock = async (vid: number) => {
    try {
      await shopFetch(`/api/shop/restock/${vid}`, { method: "POST" });
      toast(t.restockSubscribed);
    } catch (e: any) {
      toast(e.message, "error");
    }
  };

  return (
    <div className="rise-in">
      <div className="grid grid-cols-1 lg:grid-cols-2 lg:gap-8 lg:px-4 lg:pt-6">
        {/* Left: Swipeable Editorial Photo Gallery */}
        <div>
          <div
            className="relative aspect-[3/4] max-h-[560px] w-full overflow-hidden bg-[#e6dccb] select-none"
            onTouchStart={(e) => setTouchStartX(e.touches[0].clientX)}
            onTouchEnd={(e) => {
              if (touchStartX === null || images.length < 2) return;
              const dx = e.changedTouches[0].clientX - touchStartX;
              if (dx < -40) setImgIdx((i) => (i + 1) % images.length);
              if (dx > 40)
                setImgIdx((i) => (i - 1 + images.length) % images.length);
              setTouchStartX(null);
            }}
          >
            <ProductImage
              src={images[imgIdx]}
              alt={name}
              className="h-full w-full"
            />

            {images.length > 1 && (
              <div className="absolute bottom-3 left-0 right-0 flex justify-center gap-1.5">
                {images.map((_, idx) => (
                  <button
                    key={idx}
                    type="button"
                    aria-label={`Rasm ${idx + 1}`}
                    onClick={() => setImgIdx(idx)}
                    className={`h-1.5 rounded-full transition-all border-0 cursor-pointer ${
                      idx === imgIdx
                        ? "w-6 bg-[#172641]"
                        : "w-1.5 bg-[#172641]/30"
                    }`}
                  />
                ))}
              </div>
            )}
          </div>

          {images.length > 1 && (
            <div className="flex gap-2 overflow-x-auto px-4 pt-3 lg:px-0">
              {images.map((img, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setImgIdx(i)}
                  className={`h-16 w-12 shrink-0 overflow-hidden border-2 transition cursor-pointer p-0 ${
                    i === imgIdx
                      ? "border-[#172641]"
                      : "border-transparent opacity-60"
                  }`}
                >
                  <ProductImage src={img} alt="" className="h-full w-full" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Right: Editorial Product Details */}
        <div className="px-4 pt-5 lg:px-0 lg:pt-0">
          <div className="text-[10px] font-bold uppercase tracking-[.22em] text-[#8a6c43]">
            {product.sale_type === "stock" ? t.inStockBadge : t.preorderBadge}
            {product.material ? ` · ${product.material}` : ""}
          </div>

          <h1 className="mt-2 font-display text-[28px] leading-[1.1] text-[#172641]">
            {name}
          </h1>

          <div className="mt-2 flex items-center justify-between">
            <span className="text-[18px] font-bold text-[#172641]">
              {formatPrice(product.price)}
            </span>
            {product.sale_type === "stock" && product.stock_total !== null && (
              <span className="text-xs font-semibold text-[#8a6c43]">
                {t.stockLeft}: {product.stock_total} {t.pcs}
              </span>
            )}
          </div>

          {desc && (
            <p className="mt-4 whitespace-pre-line text-[13px] leading-6 text-[#172641]/80">
              {desc}
            </p>
          )}

          {/* Variants & Size Chart */}
          <div className="mt-6 border-t border-[#172641]/12 pt-5">
            <div className="mb-2.5 flex flex-wrap items-center justify-between gap-2">
              <span className="text-[10px] font-bold uppercase tracking-[.18em] text-[#172641]">
                {t.size} / {t.color}
              </span>
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => setShowSizeCalc((v) => !v)}
                  className="text-[11px] font-bold text-[#8a6c43] underline underline-offset-4 bg-transparent border-0 cursor-pointer"
                >
                  {lang === "ru" ? "📏 Подобрать размер" : "📏 O'lchamimni aniqlash"}
                </button>
                {product.size_chart && product.size_chart.length > 0 && (
                  <button
                    type="button"
                    onClick={() => setShowChart((v) => !v)}
                    className="text-[11px] font-semibold text-[#172641] underline underline-offset-4 bg-transparent border-0 cursor-pointer"
                  >
                    {t.sizeChart}
                  </button>
                )}
              </div>
            </div>

            {/* Smart Size Recommender Calculator */}
            {showSizeCalc && (
              <div className="mb-4 border border-[#172641]/20 bg-[#fbf8f2] p-3.5 space-y-3 rise-in">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-[.16em] text-[#8a6c43]">
                    {lang === "ru"
                      ? "Калькулятор размера (Рост и Вес)"
                      : "Aqlli o'lcham tavsiyasi (Bo'y va Vazn)"}
                  </span>
                  <button
                    type="button"
                    onClick={() => setShowSizeCalc(false)}
                    className="text-xs text-[#172641]/50 bg-transparent border-0 cursor-pointer"
                  >
                    ✕
                  </button>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <label className="text-[10px] font-semibold text-[#172641]/70">
                    {lang === "ru" ? "Рост (см)" : "Bo'yingiz (sm)"}
                    <input
                      type="number"
                      min={145}
                      max={215}
                      value={heightCm}
                      onChange={(e) => setHeightCm(e.target.value)}
                      className="mt-1 h-9 w-full border border-[#172641]/20 bg-white px-2.5 text-xs font-semibold text-[#172641]"
                    />
                  </label>
                  <label className="text-[10px] font-semibold text-[#172641]/70">
                    {lang === "ru" ? "Вес (кг)" : "Vazningiz (kg)"}
                    <input
                      type="number"
                      min={40}
                      max={160}
                      value={weightKg}
                      onChange={(e) => setWeightKg(e.target.value)}
                      className="mt-1 h-9 w-full border border-[#172641]/20 bg-white px-2.5 text-xs font-semibold text-[#172641]"
                    />
                  </label>
                  <label className="text-[10px] font-semibold text-[#172641]/70">
                    {lang === "ru" ? "Посадка" : "Bichim"}
                    <select
                      value={fitPref}
                      onChange={(e) => setFitPref(e.target.value as any)}
                      className="mt-1 h-9 w-full border border-[#172641]/20 bg-white px-2 text-xs font-semibold text-[#172641]"
                    >
                      <option value="regular">
                        {lang === "ru" ? "Классика" : "Klassik"}
                      </option>
                      <option value="relaxed">
                        {lang === "ru" ? "Свободно" : "Erkinroq"}
                      </option>
                    </select>
                  </label>
                </div>
                <div className="flex flex-wrap items-center justify-between gap-2 border-t border-[#172641]/10 pt-2.5">
                  <div className="text-xs text-[#172641]">
                    {lang === "ru" ? "Рекомендуемый размер: " : "Tavsiya etilgan o'lcham: "}
                    <strong className="font-display text-base text-[#172641]">
                      {rec.letter} ({rec.numeric})
                    </strong>
                  </div>
                  {rec.matchingVariant && (
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedVariantId(rec.matchingVariant.id);
                        setShowSizeCalc(false);
                      }}
                      className="bg-[#172641] px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-[#f4efe5] border-0 cursor-pointer"
                    >
                      {lang === "ru"
                        ? `Выбрать ${rec.matchingVariant.size}`
                        : `${rec.matchingVariant.size} ni tanlash`}
                    </button>
                  )}
                </div>
              </div>
            )}

            {availableVariants.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {availableVariants.map((v: any) => {
                  const active = selectedVariantId === v.id;
                  return (
                    <button
                      key={v.id}
                      type="button"
                      onClick={() => setSelectedVariantId(v.id)}
                      className={`min-h-[44px] rounded-xl border px-4 py-2 text-[12px] font-semibold transition-all duration-200 cursor-pointer active:scale-95 ${
                        active
                          ? "border-[#c5a676] bg-[#172641] text-[#faf7f2] shadow-[0_4px_14px_rgba(23,38,65,0.25)] ring-2 ring-[#c5a676] ring-offset-2 ring-offset-[#fbf8f2]"
                          : "border-[#dccab0] bg-white text-[#172641] shadow-xs hover:border-[#c5a676] hover:shadow-[0_4px_12px_rgba(197,166,118,0.2)] hover:-translate-y-0.5"
                      }`}
                    >
                      <span>
                        {v.size} {v.color ? `· ${v.color}` : ""}
                      </span>
                      {product.sale_type === "stock" && v.stock != null && (
                        <span className="ml-1.5 text-[10px] opacity-75">
                          ({v.stock})
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className="border border-[#172641]/15 bg-[#fbf8f2] p-3 text-xs font-semibold text-[#a3463c]">
                {t.soldOut}
              </div>
            )}

            {/* Size Chart Table (cm) */}
            {(showChart ||
              (product.size_chart && product.size_chart.length > 0)) && (
              <div className="mt-4 border border-[#172641]/12 bg-[#fbf8f2] overflow-x-auto">
                <table className="w-full text-[11px] border-collapse">
                  <thead className="border-b border-[#172641]/10 text-[9px] uppercase tracking-wider text-[#172641]/60">
                    <tr>
                      <th className="px-3 py-2 text-left">{t.size}</th>
                      <th className="px-3 py-2 text-center">{t.chest}</th>
                      <th className="px-3 py-2 text-center">{t.waist}</th>
                      <th className="px-3 py-2 text-center">{t.length}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(product.size_chart || []).map((row: any, idx: number) => (
                      <tr
                        key={idx}
                        className="border-t border-[#172641]/10 text-center"
                      >
                        <td className="px-3 py-2 text-left font-semibold">
                          {row.size}
                        </td>
                        <td className="px-3 py-2">{row.chest || "-"}</td>
                        <td className="px-3 py-2">{row.waist || "-"}</td>
                        <td className="px-3 py-2">{row.length || "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Sold-Out Restock Notification */}
            {soldOutVariants.length > 0 && (
              <div className="mt-4 border border-[#172641]/15 bg-[#fbf8f2] p-3.5 space-y-2">
                <div className="text-[10px] font-bold uppercase tracking-[.18em] text-[#8a6c43]">
                  {t.soldOut} — {t.notifyRestock}
                </div>
                <div className="flex flex-wrap gap-2">
                  {soldOutVariants.map((v: any) => (
                    <button
                      key={v.id}
                      type="button"
                      onClick={() => subscribeRestock(v.id)}
                      className="min-h-[40px] border border-[#172641]/25 bg-white px-3 py-1.5 text-xs font-semibold text-[#172641] cursor-pointer hover:bg-[#172641] hover:text-[#f4efe5]"
                    >
                      {v.size} {v.color ? `· ${v.color}` : ""} —{" "}
                      {t.notifyRestock}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {product.material && (
              <div className="mt-5 flex justify-between border-t border-[#172641]/10 pt-3 text-[12px]">
                <span className="text-[#172641]/60">{t.material}</span>
                <span className="font-semibold text-[#172641]">
                  {product.material}
                </span>
              </div>
            )}
          </div>

          {/* Add to Cart Bar */}
          {selectedVariant && (
            <div className="mt-6 flex items-center gap-2">
              <div className="flex h-12 items-center rounded-2xl border border-[#dccab0] bg-white shadow-xs overflow-hidden">
                <button
                  type="button"
                  onClick={() => setQty((q) => Math.max(1, q - 1))}
                  className="px-3.5 h-full text-base font-bold text-[#172641] bg-transparent hover:bg-[#f6f2ea] active:scale-90 transition border-0 cursor-pointer"
                >
                  −
                </button>
                <span className="w-8 text-center text-[13px] font-bold text-[#172641]">
                  {qty}
                </span>
                <button
                  type="button"
                  onClick={() => setQty((q) => q + 1)}
                  className="px-3.5 h-full text-base font-bold text-[#172641] bg-transparent hover:bg-[#f6f2ea] active:scale-90 transition border-0 cursor-pointer"
                >
                  +
                </button>
              </div>

              <button
                type="button"
                onClick={() =>
                  onAddToCart(selectedVariant.id, product.id, qty)
                }
                className="flex h-12 flex-1 items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-[#172641] via-[#223558] to-[#121c2e] hover:from-[#1f3357] hover:to-[#1a2942] px-4 text-[11px] font-bold uppercase tracking-[.16em] text-[#faf7f2] shadow-[0_6px_20px_rgba(23,38,65,0.28)] hover:shadow-[0_8px_24px_rgba(23,38,65,0.38)] hover:-translate-y-0.5 transition-all duration-200 active:scale-[.98] cursor-pointer border-0"
              >
                {t.addToCart} — {formatPrice(product.price * qty)}
              </button>

              <button
                type="button"
                aria-label={t.favorites}
                onClick={() => onToggleFav(product.id)}
                className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border border-[#dccab0] bg-white text-[#172641] shadow-xs hover:border-[#c5a676] hover:text-[#a3463c] hover:shadow-[0_4px_16px_rgba(163,70,60,0.18)] hover:-translate-y-0.5 active:scale-95 transition-all duration-200 cursor-pointer"
              >
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill={favIds.includes(product.id) ? "#a3463c" : "none"}
                  stroke={
                    favIds.includes(product.id) ? "#a3463c" : "currentColor"
                  }
                  strokeWidth="1.8"
                >
                  <path d="M12 21s-7-4.5-9.5-9A5.5 5.5 0 0 1 12 6a5.5 5.5 0 0 1 9.5 6c-2.5 4.5-9.5 9-9.5 9z" />
                </svg>
              </button>
            </div>
          )}

          {/* 1-Click Quick Order Button */}
          {selectedVariant && (
            <div className="mt-2.5">
              <button
                type="button"
                onClick={() => setShowQuickModal(true)}
                className="flex h-12 w-full items-center justify-center gap-2 rounded-2xl border-2 border-[#c5a676] bg-gradient-to-r from-[#faf5ea] via-[#f7ebd4] to-[#faf5ea] text-[11px] font-bold uppercase tracking-[.14em] text-[#172641] shadow-[0_4px_14px_rgba(197,166,118,0.2)] hover:bg-gradient-to-r hover:from-[#c5a676] hover:to-[#b38f5c] hover:text-white hover:shadow-[0_8px_24px_rgba(197,166,118,0.38)] hover:-translate-y-0.5 transition-all duration-200 active:scale-[.98] cursor-pointer"
              >
                <span className="text-sm">⚡</span>
                <span>1-klikda buyurtma (Menejer yordami)</span>
              </button>
              <div className="mt-1 text-center text-[10px] text-[#172641]/60">
                Pochta manzilini yozishga erinsangiz — telefoningizni qoldiring, o‘zimiz bog‘lanamiz.
              </div>
            </div>
          )}

          {/* Quick Order Modal */}
          {showQuickModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
              <div className="w-full max-w-sm rounded-2xl border border-border bg-[#faf8f3] p-5 shadow-2xl text-[#172641] space-y-4 rise-in">
                <div className="flex items-center justify-between border-b border-[#172641]/10 pb-3">
                  <div>
                    <div className="text-[9px] font-bold uppercase tracking-[.18em] text-[#8a6c43]">
                      Tezkor rasmiylashtirish
                    </div>
                    <h3 className="font-display text-lg font-bold">
                      ⚡ 1-Klikda buyurtma
                    </h3>
                  </div>
                  <button
                    type="button"
                    onClick={() => setShowQuickModal(false)}
                    className="h-7 w-7 rounded-full bg-[#172641]/10 text-xs font-bold border-0 cursor-pointer"
                  >
                    ✕
                  </button>
                </div>

                <div className="text-xs text-[#172641]/75">
                  <b>{product.name_uz}</b> ({selectedVariant?.size || "M"}
                  {selectedVariant?.color ? ` · ${selectedVariant.color}` : ""}) —{" "}
                  <b>{formatPrice(product.price)}</b>
                </div>

                <form
                  onSubmit={async (e) => {
                    e.preventDefault();
                    if (quickLoading) return;
                    setQuickLoading(true);
                    try {
                      const res = await shopFetch("/api/shop/quick-order", {
                        method: "POST",
                        body: JSON.stringify({
                          product_id: product.id,
                          variant_id: selectedVariantId,
                          name: quickName,
                          phone: quickPhone,
                          city: quickCity,
                          height_cm: heightCm,
                          weight_kg: weightKg,
                        }),
                      });
                      toast(
                        lang === "ru"
                          ? "Заказ принят! Менеджер свяжется с вами."
                          : "Buyurtma qabul qilindi! Menejerimiz tez orada bog‘lanadi."
                      );
                      setShowQuickModal(false);
                      navigate(`/miniapp/order/${res.code}`, {
                        state: { order: res },
                      });
                    } catch (err: any) {
                      toast(err.message, "error");
                    } finally {
                      setQuickLoading(false);
                    }
                  }}
                  className="space-y-3"
                >
                  <div>
                    <label className="block text-[10px] font-bold uppercase tracking-wider text-[#172641]/70">
                      Ismingiz *
                    </label>
                    <input
                      required
                      value={quickName}
                      onChange={(e) => setQuickName(e.target.value)}
                      placeholder="Alisher"
                      className="mt-1 h-10 w-full rounded-lg border border-[#172641]/20 bg-white px-3 text-xs text-[#172641] outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-[10px] font-bold uppercase tracking-wider text-[#172641]/70">
                      Telefon raqamingiz *
                    </label>
                    <input
                      required
                      value={quickPhone}
                      onChange={(e) => setQuickPhone(e.target.value)}
                      placeholder="+998 90 123 45 67"
                      className="mt-1 h-10 w-full rounded-lg border border-[#172641]/20 bg-white px-3 text-xs text-[#172641] outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-[10px] font-bold uppercase tracking-wider text-[#172641]/70">
                      Viloyat / Shahar (Pochta filiali uchun)
                    </label>
                    <input
                      value={quickCity}
                      onChange={(e) => setQuickCity(e.target.value)}
                      placeholder="Samarqand / Toshkent / Farg‘ona..."
                      className="mt-1 h-10 w-full rounded-lg border border-[#172641]/20 bg-white px-3 text-xs text-[#172641] outline-none"
                    />
                  </div>

                  <div className="rounded-lg bg-[#efe9dc] p-2.5 text-[11px] text-[#172641]/75">
                    💡 O‘lchamingiz: <b>{heightCm} sm</b>, <b>{weightKg} kg</b>{" "}
                    (Tavsiya: <b>{rec.letter}</b>). Menejer qo‘ng‘iroq qilganda
                    o‘lchamni yana bir bor aniqlashtirib beradi.
                  </div>

                  <button
                    type="submit"
                    disabled={quickLoading}
                    className="flex h-11 w-full items-center justify-center rounded-xl bg-[#172641] text-xs font-bold uppercase tracking-[.14em] text-[#f4efe5] border-0 cursor-pointer disabled:opacity-50"
                  >
                    {quickLoading ? "Yuborilmoqda..." : "Buyurtmani tasdiqlash →"}
                  </button>
                </form>
              </div>
            </div>
          )}

          {/* Collapsible Delivery & Return Policy */}
          <details className="group mt-5 border-t border-[#172641]/12 pt-3">
            <summary className="flex cursor-pointer list-none items-center justify-between text-[11px] font-semibold text-[#172641]">
              <span>{t.deliveryAndReturnTerms}</span>
              <span className="text-[10px] text-[#172641]/50 group-open:hidden">
                ochish
              </span>
            </summary>
            <div className="mt-3 space-y-2 text-[12px] leading-5 text-[#172641]/75">
              <p>{lang === "ru" ? content?.delivery_ru : content?.delivery_uz}</p>
              <p>{lang === "ru" ? content?.returns_ru : content?.returns_uz}</p>
            </div>
          </details>
        </div>
      </div>

      {/* Related Products */}
      {product.related && product.related.length > 0 && (
        <section className="mt-10 border-t border-[#172641]/15 px-4 pt-6">
          <div className="text-[9px] font-bold uppercase tracking-[.22em] text-[#8a6c43]">
            Kolleksiyadan
          </div>
          <h2 className="mt-1 font-display text-[22px] text-[#172641]">
            {t.relatedProducts}
          </h2>
          <div className="miniapp-product-grid mt-4">
            {product.related.map((r: any) => (
              <ProductCard
                key={r.id}
                p={r}
                isFav={favIds.includes(r.id)}
                onToggleFav={onToggleFav}
              />
            ))}
          </div>
        </section>
      )}

      {/* Complete the Look (To'liq obraz yig'ish) */}
      {product.related && product.related.length > 1 && (
        <section className="mt-10 border-t border-[#172641]/15 px-4 pt-6">
          <div className="rounded-2xl border border-[#d6bd92]/40 bg-[#faf5ea] p-5">
            <div className="text-[9px] font-bold uppercase tracking-[.2em] text-[#8a6c43]">
              🤵 SARTORIAL STYLE
            </div>
            <h3 className="mt-1 font-display text-[20px] font-medium text-[#172641]">
              To‘liq obraz yig‘ish (Complete the Look)
            </h3>
            <p className="mt-1 text-xs text-[#172641]/70">
              Ushbu kiyim bilan ideal mos tushadigan klassik modellar:
            </p>

            <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
              {product.related.slice(0, 2).map((item: any) => (
                <div
                  key={item.id}
                  className="flex items-center gap-3 rounded-xl border border-border bg-card p-3"
                >
                  <Link
                    to={`/miniapp/product/${item.id}`}
                    className="h-16 w-14 shrink-0 overflow-hidden rounded-lg bg-[#e6dccb]"
                  >
                    <ProductImage
                      src={item.thumb}
                      alt={item.name_uz}
                      className="h-full w-full object-cover"
                    />
                  </Link>
                  <div className="min-w-0 flex-1">
                    <Link
                      to={`/miniapp/product/${item.id}`}
                      className="truncate text-xs font-bold text-[#172641] no-underline hover:underline block"
                    >
                      {item.name_uz}
                    </Link>
                    <div className="text-xs font-semibold text-[#8a6c43] mt-0.5">
                      {formatPrice(item.price)}
                    </div>
                    <Link
                      to={`/miniapp/product/${item.id}`}
                      className="mt-1.5 inline-block text-[10px] font-bold uppercase tracking-wider text-[#172641] underline underline-offset-2"
                    >
                      Ko‘rish va qo‘shish →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Customer Reviews & Live Looks (Real mijozlarimizda) */}
      <section className="mt-10 border-t border-[#172641]/15 px-4 pt-6 pb-6">
        <div className="flex items-end justify-between gap-2">
          <div>
            <div className="text-[9px] font-bold uppercase tracking-[.22em] text-[#8a6c43]">
              ISBOtLANGAN SIFAT
            </div>
            <h3 className="mt-1 font-display text-[22px] text-[#172641]">
              📸 Real mijozlarimiz fikrlari (Pochta orqali)
            </h3>
          </div>
          <button
            type="button"
            onClick={() => setShowReviewModal(true)}
            className="rounded-full border border-[#172641]/25 bg-[#faf8f3] px-3.5 py-1.5 text-[10px] font-bold uppercase tracking-wider text-[#172641] cursor-pointer hover:bg-[#172641] hover:text-[#f4efe5] transition"
          >
            + Fikr bildirish
          </button>
        </div>

        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {reviews.slice(0, 3).map((rev: any) => (
            <div
              key={rev.id}
              className="flex flex-col justify-between rounded-2xl border border-[#172641]/12 bg-[#faf8f3] p-4 text-xs space-y-2.5 shadow-sm"
            >
              <div>
                <div className="flex items-center justify-between gap-1">
                  <span className="font-bold text-[#172641]">{rev.name}</span>
                  <span className="text-[#a8742a]">★★★★★</span>
                </div>
                <div className="mt-0.5 text-[10px] font-semibold text-[#397252]">
                  ✓ {rev.city}
                </div>
                <p className="mt-2 text-[#172641]/85 leading-relaxed text-[11px]">
                  «{lang === "ru" ? rev.text_ru || rev.text_uz : rev.text_uz}»
                </p>
              </div>
              <div className="text-[9px] font-semibold uppercase tracking-wider text-muted-foreground pt-1 border-t border-[#172641]/10">
                Model: {rev.item}
              </div>
            </div>
          ))}
        </div>

        {/* Review Modal */}
        {showReviewModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
            <div className="w-full max-w-sm rounded-2xl border border-border bg-[#faf8f3] p-5 shadow-2xl text-[#172641] space-y-3.5 rise-in">
              <div className="flex items-center justify-between border-b border-[#172641]/10 pb-2.5">
                <h3 className="font-display text-base font-bold">
                  ✍️ Xarid bo‘yicha fikr qoldirish
                </h3>
                <button
                  type="button"
                  onClick={() => setShowReviewModal(false)}
                  className="h-7 w-7 rounded-full bg-[#172641]/10 text-xs font-bold border-0 cursor-pointer"
                >
                  ✕
                </button>
              </div>

              <form
                onSubmit={async (e) => {
                  e.preventDefault();
                  if (revSubmitting || !revText.trim()) return;
                  setRevSubmitting(true);
                  try {
                    const newRev = await shopFetch("/api/shop/reviews", {
                      method: "POST",
                      body: JSON.stringify({
                        name: revName || "Mijoz",
                        city: revCity,
                        item: product.name_uz,
                        text: revText,
                        rating: 5,
                      }),
                    });
                    toast("Fikringiz uchun rahmat!");
                    setReviews((prev) => [newRev, ...prev]);
                    setShowReviewModal(false);
                    setRevText("");
                  } catch (err: any) {
                    toast(err.message, "error");
                  } finally {
                    setRevSubmitting(false);
                  }
                }}
                className="space-y-3"
              >
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-[#172641]/70">
                    Ismingiz
                  </label>
                  <input
                    value={revName}
                    onChange={(e) => setRevName(e.target.value)}
                    placeholder="Sardor M."
                    className="mt-1 h-9 w-full rounded-lg border border-[#172641]/20 bg-white px-3 text-xs text-[#172641] outline-none"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-[#172641]/70">
                    Viloyat / Shahar (Pochta)
                  </label>
                  <input
                    value={revCity}
                    onChange={(e) => setRevCity(e.target.value)}
                    placeholder="Samarqand / Toshkent..."
                    className="mt-1 h-9 w-full rounded-lg border border-[#172641]/20 bg-white px-3 text-xs text-[#172641] outline-none"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-[#172641]/70">
                    Fikringiz (Mato sifati, o‘lcham, pochta yetib kelishi) *
                  </label>
                  <textarea
                    required
                    rows={3}
                    value={revText}
                    onChange={(e) => setRevText(e.target.value)}
                    placeholder="Kiyim kutilganidek a'lo darajada o'tirdi..."
                    className="mt-1 w-full rounded-lg border border-[#172641]/20 bg-white p-2.5 text-xs text-[#172641] outline-none resize-none"
                  />
                </div>
                <button
                  type="submit"
                  disabled={revSubmitting}
                  className="flex h-10 w-full items-center justify-center rounded-xl bg-[#172641] text-xs font-bold uppercase tracking-[.14em] text-[#f4efe5] border-0 cursor-pointer disabled:opacity-50"
                >
                  {revSubmitting ? "Yuborilmoqda..." : "Fikrni yuborish"}
                </button>
              </form>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

// ---------------- CART SCREEN ----------------
function CartScreen({
  cart,
  onUpdateCart,
  onCheckoutClick,
}: {
  cart: { items: any[]; total: number };
  onUpdateCart: (items: { variant_id: number; qty: number }[]) => Promise<any>;
  onCheckoutClick: () => void;
}) {
  const { lang, t } = useLang();
  const navigate = useNavigate();

  const changeQty = (variant_id: number, delta: number) => {
    const next = cart.items
      .map((i) =>
        i.variant_id === variant_id
          ? { variant_id, qty: i.qty + delta }
          : { variant_id: i.variant_id, qty: i.qty }
      )
      .filter((i) => i.qty > 0);
    onUpdateCart(next);
  };

  const removeRow = (variant_id: number) => {
    const next = cart.items
      .filter((i) => i.variant_id !== variant_id)
      .map((i) => ({ variant_id: i.variant_id, qty: i.qty }));
    onUpdateCart(next);
  };

  if (cart.items.length === 0) {
    return (
      <div className="px-6 py-20 text-center rise-in">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full border border-[#172641]/20">
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
          >
            <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z" />
            <line x1="3" y1="6" x2="21" y2="6" />
            <path d="M16 10a4 4 0 0 1-8 0" />
          </svg>
        </div>
        <h1 className="mt-5 font-display text-[26px] text-[#172641]">
          {t.emptyCart}
        </h1>
        <p className="mt-2 text-[12px] text-[#172641]/60">
          Kolleksiyadan o‘zingizga mosini tanlang.
        </p>
        <Link
          to="/miniapp/catalog"
          className="mt-7 inline-block bg-[#172641] px-7 py-3.5 text-[11px] font-bold uppercase tracking-[.16em] text-[#f4efe5] no-underline"
        >
          {t.catalog}
        </Link>
      </div>
    );
  }

  return (
    <div className="px-4 pt-5 max-w-3xl mx-auto rise-in">
      <h1 className="font-display text-[30px] text-[#172641]">{t.cart}</h1>

      <div className="mt-4 divide-y divide-[#172641]/12 border-y border-[#172641]/12">
        {cart.items.map((item) => (
          <div key={item.variant_id} className="flex gap-3.5 py-4">
            <Link
              to={`/miniapp/product/${item.product_id}`}
              className="h-24 w-[72px] shrink-0 overflow-hidden bg-[#e6dccb] block"
            >
              <ProductImage
                src={item.thumb}
                alt={item.name_uz}
                className="h-full w-full"
              />
            </Link>

            <div className="min-w-0 flex-1">
              <div className="flex justify-between gap-2">
                <Link
                  to={`/miniapp/product/${item.product_id}`}
                  className="line-clamp-2 font-display text-[16px] font-semibold text-[#172641] no-underline"
                >
                  {lang === "ru" ? item.name_ru : item.name_uz}
                </Link>
                <button
                  type="button"
                  onClick={() => removeRow(item.variant_id)}
                  aria-label={t.remove}
                  className="shrink-0 p-1 text-[#172641]/50 hover:text-[#a3463c] bg-transparent border-0 cursor-pointer text-xs"
                >
                  {t.remove}
                </button>
              </div>

              <div className="mt-1 text-[11px] text-[#172641]/60">
                {item.size} {item.color ? `· ${item.color}` : ""} ·{" "}
                {item.sale_type === "stock" ? t.inStockBadge : t.preorderBadge}
              </div>

              <div className="mt-2.5 flex items-center justify-between">
                <div className="flex items-center border border-[#172641]/20 bg-[#fbf8f2]">
                  <button
                    type="button"
                    onClick={() => changeQty(item.variant_id, -1)}
                    className="px-2.5 py-1 text-xs font-bold text-[#172641] bg-transparent border-0 cursor-pointer"
                  >
                    −
                  </button>
                  <span className="w-6 text-center text-[12px] font-semibold">
                    {item.qty}
                  </span>
                  <button
                    type="button"
                    onClick={() => changeQty(item.variant_id, 1)}
                    disabled={item.qty >= item.max_qty}
                    className="px-2.5 py-1 text-xs font-bold text-[#172641] bg-transparent border-0 cursor-pointer disabled:opacity-30"
                  >
                    +
                  </button>
                </div>
                <span className="text-[13px] font-bold text-[#172641]">
                  {formatPrice(item.price * item.qty)}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-5 flex items-baseline justify-between">
        <span className="text-[11px] font-bold uppercase tracking-[.16em] text-[#172641]/60">
          {t.total}
        </span>
        <span className="font-display text-[26px] font-medium text-[#172641]">
          {formatPrice(cart.total)}
        </span>
      </div>
      <p className="mt-1 text-[11px] text-[#172641]/55">
        To‘lov va yetkazish tafsilotlari buyurtmadan so‘ng menejer bilan
        kelishiladi.
      </p>

      <button
        type="button"
        onClick={() => {
          onCheckoutClick();
          navigate("/miniapp/checkout");
        }}
        className="mt-6 h-12 w-full bg-[#172641] text-[11px] font-bold uppercase tracking-[.16em] text-[#f4efe5] cursor-pointer border-0"
      >
        {t.checkout} →
      </button>
    </div>
  );
}

// ---------------- CHECKOUT SCREEN ----------------
function CheckoutScreen({
  cart,
  customer,
  content,
  onOrderCreated,
}: {
  cart: { items: any[]; total: number };
  customer: any;
  content: any;
  onOrderCreated: (order: any) => void;
}) {
  const { lang, t } = useLang();
  const { toast } = useToast();
  const [name, setName] = useState(
    customer?.name && !customer.name.startsWith("#") ? customer.name : ""
  );
  const [phone, setPhone] = useState(customer?.phone || "");
  const [city, setCity] = useState("Toshkent");
  const [address, setAddress] = useState("");
  const [comment, setComment] = useState("");
  const [delivery, setDelivery] = useState<"courier" | "pickup">("courier");
  const [promoCode, setPromoCode] = useState("");
  const [promoPercent, setPromoPercent] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [idemKey] = useState(
    () =>
      "wm-" +
      Date.now().toString(36) +
      "-" +
      Math.random().toString(36).slice(2, 10)
  );

  const checkPromo = async () => {
    if (!promoCode.trim()) return;
    try {
      const r = await shopFetch("/api/shop/promo/check", {
        method: "POST",
        body: JSON.stringify({ code: promoCode }),
      });
      setPromoPercent(r.percent);
      toast(`${r.code}: -${r.percent}%`);
    } catch (e: any) {
      setPromoPercent(0);
      toast(e.message, "error");
    }
  };

  const discount = Math.floor((cart.total * promoPercent) / 100);
  const finalTotal = cart.total - discount;
  const advancePct = Number(content?.advance_pct || 30);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    try {
      const order = await shopFetch("/api/shop/orders", {
        method: "POST",
        headers: { "Idempotency-Key": idemKey },
        body: JSON.stringify({
          name,
          phone,
          city,
          address,
          comment,
          delivery,
          promo_code: promoPercent > 0 ? promoCode : "",
        }),
      });
      onOrderCreated(order);
    } catch (err: any) {
      toast(err.message, "error");
    } finally {
      setSubmitting(false);
    }
  };

  const fieldCls =
    "mt-1 h-11 w-full border border-[#172641]/20 bg-[#fbf8f2] px-3 text-[13px] text-[#172641] outline-none focus:border-[#172641]";

  return (
    <form
      onSubmit={submit}
      className="px-4 pt-5 max-w-xl mx-auto space-y-4 rise-in"
    >
      <div>
        <div className="text-[10px] font-bold uppercase tracking-[.2em] text-[#8a6c43]">
          WHITMORE CHECKOUT
        </div>
        <h1 className="mt-1 font-display text-[28px] text-[#172641]">
          {t.checkout}
        </h1>
      </div>

      <div className="space-y-3.5 border-t border-[#172641]/15 pt-4">
        <div>
          <label
            htmlFor="co-name"
            className="block text-[10px] font-bold uppercase tracking-[.14em] text-[#172641]/70"
          >
            {t.yourName} *
          </label>
          <input
            id="co-name"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className={fieldCls}
          />
        </div>

        <div>
          <label
            htmlFor="co-phone"
            className="block text-[10px] font-bold uppercase tracking-[.14em] text-[#172641]/70"
          >
            {customer?.is_telegram ? t.phoneOptionalTg : `${t.phone} *`}
          </label>
          <input
            id="co-phone"
            required={!customer?.is_telegram}
            placeholder="+998 90 123 45 67"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            className={fieldCls}
          />
        </div>

        <div>
          <span className="block text-[10px] font-bold uppercase tracking-[.14em] text-[#172641]/70 mb-1.5">
            {t.deliveryMethod}
          </span>
          <div className="grid grid-cols-2 gap-2">
            {(["courier", "pickup"] as const).map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => setDelivery(m)}
                className={`border py-3 text-[12px] font-semibold transition cursor-pointer ${
                  delivery === m
                    ? "border-[#172641] bg-[#172641] text-[#f4efe5]"
                    : "border-[#172641]/20 bg-[#fbf8f2] text-[#172641]"
                }`}
              >
                {m === "courier" ? t.courier : t.pickup}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label
            htmlFor="co-city"
            className="block text-[10px] font-bold uppercase tracking-[.14em] text-[#172641]/70"
          >
            {t.city}
          </label>
          <input
            id="co-city"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            className={fieldCls}
          />
        </div>

        {delivery === "courier" && (
          <div>
            <label
              htmlFor="co-address"
              className="block text-[10px] font-bold uppercase tracking-[.14em] text-[#172641]/70"
            >
              {t.address} *
            </label>
            <input
              id="co-address"
              required
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              className={fieldCls}
            />
          </div>
        )}

        <div>
          <label
            htmlFor="co-comment"
            className="block text-[10px] font-bold uppercase tracking-[.14em] text-[#172641]/70"
          >
            {t.comment}
          </label>
          <textarea
            id="co-comment"
            rows={2}
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            className={`${fieldCls} h-auto py-2`}
          />
        </div>

        {/* Promo Code */}
        <div className="flex gap-2 items-end pt-1">
          <div className="flex-1">
            <label
              htmlFor="co-promo"
              className="block text-[10px] font-bold uppercase tracking-[.14em] text-[#172641]/70"
            >
              {t.promoCode}
            </label>
            <input
              id="co-promo"
              placeholder="WELCOME10"
              value={promoCode}
              onChange={(e) => setPromoCode(e.target.value.toUpperCase())}
              className={fieldCls}
            />
          </div>
          <button
            type="button"
            onClick={checkPromo}
            className="h-11 border border-[#172641]/25 bg-[#fbf8f2] px-4 text-xs font-bold text-[#172641] cursor-pointer"
          >
            {t.applyPromo}
          </button>
        </div>
      </div>

      {/* Delivery & Return Rules */}
      <div className="border border-[#172641]/15 bg-[#fbf8f2] p-4 space-y-1.5 text-xs text-[#172641]/75">
        <div className="text-[10px] font-bold uppercase tracking-[.18em] text-[#8a6c43]">
          {t.deliveryAndReturnTerms}
        </div>
        <p>{lang === "ru" ? content?.delivery_ru : content?.delivery_uz}</p>
        <p>{lang === "ru" ? content?.returns_ru : content?.returns_uz}</p>
      </div>

      {/* Summary & Submit */}
      <div className="border-t border-[#172641]/15 pt-4 space-y-2">
        <div className="flex justify-between text-xs">
          <span className="text-[#172641]/60">{t.subtotal}</span>
          <span className="font-semibold">{formatPrice(cart.total)}</span>
        </div>
        {discount > 0 && (
          <div className="flex justify-between text-xs text-[#397252]">
            <span>{t.discount}</span>
            <span>−{formatPrice(discount)}</span>
          </div>
        )}
        <div className="flex justify-between items-baseline pt-2 border-t border-[#172641]/12">
          <span className="text-xs font-bold uppercase tracking-wider">
            {t.total}
          </span>
          <span className="font-display text-[24px] font-medium">
            {formatPrice(finalTotal)}
          </span>
        </div>
        <div className="flex justify-between text-xs text-[#172641]/60">
          <span>Oldindan to'lov ({advancePct}%)</span>
          <span>
            {formatPrice(Math.round((finalTotal * advancePct) / 100))}
          </span>
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="mt-3 h-12 w-full bg-[#172641] text-[11px] font-bold uppercase tracking-[.16em] text-[#f4efe5] disabled:opacity-50 cursor-pointer border-0"
        >
          {submitting ? "Yuborilmoqda…" : t.placeOrder}
        </button>
      </div>
    </form>
  );
}

// ---------------- ORDER RESULT SCREEN (REPLIT EDITORIAL) ----------------
const TRACKER_STEPS: { key: string; uz: string; ru: string; desc_uz: string; desc_ru: string }[] = [
  { key: "new", uz: "Yangi buyurtma", ru: "Новый заказ", desc_uz: "Buyurtma qabul qilindi", desc_ru: "Заказ принят" },
  { key: "awaiting_payment", uz: "To'lov kutilmoqda", ru: "Ожидает оплаты", desc_uz: "Oldindan to'lov (avans) tekshirilmoqda", desc_ru: "Проверка предоплаты" },
  { key: "paid", uz: "To'langan", ru: "Оплачен", desc_uz: "Avans to'lovi tasdiqlandi", desc_ru: "Предоплата подтверждена" },
  { key: "ordered_china", uz: "Xitoyda buyurtma berildi", ru: "Заказан в Китае", desc_uz: "Fabrika va yetkazib beruvchiga buyurtma berildi", desc_ru: "Заказано на фабрике" },
  { key: "china_warehouse", uz: "Xitoy omborida", ru: "На складе в Китае", desc_uz: "Sifat nazorati va qadoqlash", desc_ru: "Проверка качества и упаковка" },
  { key: "in_transit", uz: "Yo'lda (Kargo)", ru: "В пути (Карго)", desc_uz: "Xitoydan O'zbekistonga jo'natildi", desc_ru: "Отправлено из Китая в Узбекистан" },
  { key: "in_uz", uz: "O'zbekistonda", ru: "В Узбекистане", desc_uz: "Toshkent saralash markazida", desc_ru: "В сортировочном центре Ташкента" },
  { key: "delivered", uz: "Yetkazildi", ru: "Доставлен", desc_uz: "Mijozga topshirildi", desc_ru: "Вручено клиенту" },
];

function OrderResultScreen({
  content,
  onContactClick,
}: {
  content?: any;
  onContactClick: () => void;
}) {
  const { code } = useParams();
  const { lang, t } = useLang();
  const { toast } = useToast();
  const [order, setOrder] = useState<any>(null);
  const [admins, setAdmins] = useState<any[]>([]);
  const [assignedId, setAssignedId] = useState<number | null>(null);
  const [uploadingReceipt, setUploadingReceipt] = useState(false);

  useEffect(() => {
    if (!code) return;
    Promise.all([
      shopFetch(`/api/shop/orders/${code}`),
      shopFetch(`/api/shop/orders/${code}/admins`),
    ])
      .then(([ord, adm]) => {
        setOrder(ord);
        setAdmins(adm.admins || []);
        setAssignedId(adm.assigned_id);
      })
      .catch((e) => toast(e.message, "error"));
  }, [code]);

  if (!order) {
    return (
      <div className="p-4">
        <SkeletonList count={2} />
      </div>
    );
  }

  const chooseAdmin = async (adminId: number) => {
    try {
      const updated = await shopFetch(`/api/shop/orders/${code}/assign`, {
        method: "POST",
        body: JSON.stringify({ admin_id: adminId }),
      });
      setOrder(updated);
      setAssignedId(adminId);
    } catch (e: any) {
      toast(e.message, "error");
    }
  };

  const uploadReceipt = async (file: File) => {
    setUploadingReceipt(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const token = getShopToken();
      const res = await fetch(`/api/shop/orders/${code}/receipt`, {
        method: "POST",
        headers: token ? { "x-shop-token": token } : {},
        body: fd,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Xatolik");
      setOrder(data);
      toast(
        lang === "ru"
          ? "Чек загружен и отправлен администратору!"
          : "To'lov cheki yuklandi va adminga yuborildi!"
      );
    } catch (e: any) {
      toast(e.message, "error");
    } finally {
      setUploadingReceipt(false);
    }
  };

  const activeAdmin =
    admins.find((a) => a.id === assignedId) || order.assigned_admin;
  const tgUrl = activeAdmin?.username
    ? `https://t.me/${activeAdmin.username}?text=${encodeURIComponent(
        order.summary
      )}`
    : "#";

  const cardNumber = content?.payment_card_number || "8600 1234 5678 9012";
  const cardHolder = content?.payment_card_holder || "WHITMORE MENSWEAR";
  const advancePct = Number(order.advance_pct || content?.advance_pct || 30);
  const advanceAmount =
    order.advance_amount ?? Math.round((order.total * advancePct) / 100);
  const currentStepIdx = Math.max(
    0,
    TRACKER_STEPS.findIndex((s) => s.key === order.status)
  );
  const isPaidOrLater = currentStepIdx >= 2;

  return (
    <div className="mx-auto max-w-xl px-5 pt-8 pb-8 space-y-6 rise-in">
      <div className="text-center">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-[#172641] text-[#d6bd92]">
          <svg
            width="26"
            height="26"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.2"
          >
            <polyline points="20 6 9 17 4 12" />
          </svg>
        </div>
        <div className="mt-5 text-[10px] font-bold uppercase tracking-[.22em] text-[#8a6c43]">
          {t.orderCreatedTitle}
        </div>
        <h1 className="mt-2 font-display text-[34px] text-[#172641]">
          {order.code}
        </h1>
        <div className="mt-1 text-[16px] font-bold text-[#172641]">
          {formatPrice(order.total)}
        </div>
        <div className="mt-2 flex justify-center">
          <StatusBadge status={order.status} />
        </div>
      </div>

      {/* 1) VISUAL CARGO TRACKER (XITOY -> O'ZBEKISTON) */}
      <div className="border border-[#172641]/15 bg-[#fbf8f2] p-4 space-y-3">
        <div className="flex items-center justify-between border-b border-[#172641]/10 pb-2.5">
          <div>
            <div className="text-[10px] font-bold uppercase tracking-[.18em] text-[#8a6c43]">
              {lang === "ru" ? "Отслеживание заказа" : "Buyurtma holati va Kargo"}
            </div>
            <div className="font-display text-lg text-[#172641]">
              {lang === "ru" ? "Маршрут: Китай → Узбекистан" : "Yo'nalish: Xitoy → O'zbekiston"}
            </div>
          </div>
          {order.tracking && (
            <div className="text-right">
              <div className="text-[9px] font-bold uppercase tracking-wider text-[#172641]/60">
                Trek-kod
              </div>
              <div className="font-mono text-xs font-bold text-[#172641] bg-[#d6bd92]/35 px-2 py-0.5">
                {order.tracking}
              </div>
            </div>
          )}
        </div>

        {order.status === "cancelled" ? (
          <div className="bg-[#a3463c]/10 border border-[#a3463c]/30 p-3 text-xs font-semibold text-[#a3463c]">
            {lang === "ru" ? "Заказ отменён" : "Buyurtma bekor qilingan"}
          </div>
        ) : (
          <div className="space-y-2.5 pt-1">
            {TRACKER_STEPS.map((st, idx) => {
              const done = idx < currentStepIdx;
              const current = idx === currentStepIdx;
              return (
                <div key={st.key} className="flex items-start gap-3">
                  <div className="flex flex-col items-center">
                    <div
                      className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[11px] font-bold ${
                        done
                          ? "bg-[#397252] text-white"
                          : current
                          ? "bg-[#172641] text-[#d6bd92] ring-2 ring-[#d6bd92]"
                          : "border border-[#172641]/20 bg-white text-[#172641]/40"
                      }`}
                    >
                      {done ? "✓" : idx + 1}
                    </div>
                    {idx < TRACKER_STEPS.length - 1 && (
                      <div
                        className={`h-4 w-[2px] ${
                          done ? "bg-[#397252]" : "bg-[#172641]/15"
                        }`}
                      />
                    )}
                  </div>
                  <div className="min-w-0 flex-1 pb-0.5">
                    <div
                      className={`text-xs font-bold ${
                        current
                          ? "text-[#172641]"
                          : done
                          ? "text-[#397252]"
                          : "text-[#172641]/45"
                      }`}
                    >
                      {lang === "ru" ? st.ru : st.uz}
                    </div>
                    <div className="text-[11px] text-[#172641]/60">
                      {lang === "ru" ? st.desc_ru : st.desc_uz}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 2) 30% ADVANCE PAYMENT & RECEIPT UPLOAD */}
      {order.status !== "cancelled" && (
        <div className="border border-[#172641]/20 bg-[#172641] p-5 text-[#f4efe5] space-y-4">
          <div className="flex items-start justify-between gap-2 border-b border-white/15 pb-3">
            <div>
              <div className="text-[10px] font-bold uppercase tracking-[.2em] text-[#d6bd92]">
                {lang === "ru"
                  ? `Предоплата (${advancePct}%)`
                  : `Oldindan to'lov (${advancePct}% Avans)`}
              </div>
              <div className="mt-1 font-display text-2xl text-white">
                {formatPrice(advanceAmount)}
              </div>
            </div>
            <span
              className={`px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider ${
                isPaidOrLater
                  ? "bg-[#397252] text-white"
                  : order.receipt_photo
                  ? "bg-[#d6bd92] text-[#172641]"
                  : "bg-white/15 text-[#f4efe5]"
              }`}
            >
              {isPaidOrLater
                ? lang === "ru"
                  ? "✅ Оплачено"
                  : "✅ To'lov tasdiqlangan"
                : order.receipt_photo
                ? lang === "ru"
                  ? "⏳ Чек на проверке"
                  : "⏳ Chek tekshirilmoqda"
                : lang === "ru"
                ? "Ожидает оплаты"
                : "To'lov kutilmoqda"}
            </span>
          </div>

          <div className="space-y-2 rounded bg-white/[.06] p-3.5 border border-white/10">
            <div className="text-[10px] uppercase tracking-wider text-white/60">
              {lang === "ru" ? "Карта для перевода" : "To'lov uchun karta raqami"}
            </div>
            <div className="flex items-center justify-between gap-2">
              <span className="font-mono text-base font-bold tracking-wider text-[#d6bd92]">
                {cardNumber}
              </span>
              <button
                type="button"
                onClick={() => {
                  navigator.clipboard?.writeText(cardNumber.replace(/\s+/g, ""));
                  toast(t.copied);
                }}
                className="bg-[#d6bd92] px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-[#172641] border-0 cursor-pointer"
              >
                {lang === "ru" ? "Копировать" : "Nusxalash"}
              </button>
            </div>
            <div className="text-xs text-white/75">{cardHolder}</div>
          </div>

          {order.receipt_photo && (
            <div className="flex items-center gap-3 rounded bg-white/[.05] p-2.5 border border-white/10">
              <img
                src={`/uploads/${order.receipt_photo}`}
                alt="Chek"
                className="h-14 w-14 object-cover border border-white/20"
              />
              <div className="text-xs text-white/85">
                <div className="font-bold text-[#d6bd92]">
                  {lang === "ru" ? "Чек загружен" : "To'lov cheki yuklangan"}
                </div>
                <div className="text-[11px] text-white/65">
                  {isPaidOrLater
                    ? lang === "ru"
                      ? "Администратор подтвердил вашу оплату."
                      : "Admin to'lovingizni tasdiqladi."
                    : lang === "ru"
                    ? "Отправлено администратору в Telegram."
                    : "Telegram orqali adminga yuborildi."}
                </div>
              </div>
            </div>
          )}

          {!isPaidOrLater && (
            <label className="flex h-11 w-full items-center justify-center gap-2 bg-[#d6bd92] text-[11px] font-bold uppercase tracking-[.14em] text-[#172641] cursor-pointer">
              <span>
                {uploadingReceipt
                  ? lang === "ru"
                    ? "Загрузка чека…"
                    : "Chek yuklanmoqda…"
                  : order.receipt_photo
                  ? lang === "ru"
                    ? "📸 Загрузить другой чек"
                    : "📸 Boshqa chek yuklash"
                  : lang === "ru"
                  ? "📸 Загрузить скриншот чека"
                  : "📸 To'lov chekini (skrinshot) yuklash"}
              </span>
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp"
                className="hidden"
                disabled={uploadingReceipt}
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) uploadReceipt(f);
                  e.target.value = "";
                }}
              />
            </label>
          )}
        </div>
      )}

      {/* Ready Message Summary */}
      <div className="space-y-2.5">
        <div className="text-[10px] font-bold uppercase tracking-[.16em] text-[#172641]/60">
          {t.readyMessage}
        </div>
        <pre className="max-h-56 overflow-auto whitespace-pre-wrap border border-[#172641]/15 bg-[#fbf8f2] p-4 text-left font-sans text-xs leading-5 text-[#172641]">
          {order.summary}
        </pre>
        <button
          type="button"
          onClick={() => {
            navigator.clipboard?.writeText(order.summary);
            toast(t.copied);
          }}
          className="h-11 w-full border border-[#172641]/25 bg-[#fbf8f2] text-[11px] font-bold uppercase tracking-[.12em] text-[#172641] cursor-pointer"
        >
          {t.copyMessage}
        </button>
      </div>

      {/* Assigned Admin Selector */}
      <div className="space-y-3 border-t border-[#172641]/15 pt-5">
        <div className="text-[10px] font-bold uppercase tracking-[.16em] text-[#172641]/60">
          {t.assignedAdmin}
        </div>
        <div className="space-y-2">
          {admins.map((a) => {
            const isSelected = a.id === assignedId;
            return (
              <div
                key={a.id}
                onClick={() => chooseAdmin(a.id)}
                className={`flex items-center justify-between border p-3 cursor-pointer transition ${
                  isSelected
                    ? "border-[#172641] bg-[#fbf8f2]"
                    : "border-[#172641]/15 bg-white/70"
                }`}
              >
                <div className="flex items-center gap-3">
                  {a.avatar ? (
                    <img
                      src={`/uploads/${a.avatar}`}
                      alt={a.full_name}
                      className="h-10 w-10 rounded-full object-cover border border-[#172641]/20"
                    />
                  ) : (
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#172641] font-display text-sm text-[#d6bd92]">
                      {a.full_name?.slice(0, 1)}
                    </div>
                  )}
                  <div>
                    <div className="text-sm font-bold text-[#172641]">
                      {a.full_name}
                    </div>
                    <div className="text-xs text-[#172641]/60">
                      @{a.username}
                    </div>
                  </div>
                </div>
                <span
                  className={`px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider ${
                    isSelected
                      ? "bg-[#172641] text-[#f4efe5]"
                      : "border border-[#172641]/20 text-[#172641]"
                  }`}
                >
                  {isSelected ? "Tanlangan" : "Tanlash"}
                </span>
              </div>
            );
          })}
        </div>

        {activeAdmin?.username && (
          <a
            href={tgUrl}
            target="_blank"
            rel="noreferrer"
            onClick={() => onContactClick()}
            className="flex h-12 w-full items-center justify-center bg-[#172641] text-[11px] font-bold uppercase tracking-[.14em] text-[#f4efe5] no-underline"
          >
            {t.writeToAdmin} (@{activeAdmin.username})
          </a>
        )}
      </div>
    </div>
  );
}

// ---------------- ORDERS SCREEN (BUYURTMALARIM & KARGO KUZATUV) ----------------
function OrdersScreen({ content }: { content: any }) {
  const { lang, t } = useLang();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [orders, setOrders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [lookupCode, setLookupCode] = useState("");
  const [searching, setSearching] = useState(false);

  const loadOrders = () => {
    setLoading(true);
    shopFetch("/api/shop/orders")
      .then((res) => setOrders(Array.isArray(res) ? res : []))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadOrders();
  }, []);

  const handleLookup = async (e: React.FormEvent) => {
    e.preventDefault();
    const clean = lookupCode.trim().toUpperCase();
    if (!clean) return;
    setSearching(true);
    try {
      const found = await shopFetch(`/api/shop/orders/${encodeURIComponent(clean)}`);
      if (found?.code) {
        navigate(`/miniapp/order/${found.code}`, { state: { order: found } });
      }
    } catch {
      toast(
        lang === "ru"
          ? "Заказ с таким кодом не найден"
          : "Bunday kodli buyurtma topilmadi",
        "error"
      );
    } finally {
      setSearching(false);
    }
  };

  const stepIndex = (st: string) => {
    const list = [
      "new",
      "awaiting_payment",
      "paid",
      "ordered_china",
      "china_warehouse",
      "in_transit",
      "in_uz",
      "delivered",
    ];
    const idx = list.indexOf(st);
    if (st === "delivered" || st === "completed") return 6;
    return idx >= 0 ? idx : 0;
  };

  const contactUser = content?.contact_username?.replace(/^@/, "");

  return (
    <div className="mx-auto max-w-3xl px-4 pt-5 pb-16 space-y-6 rise-in">
      {/* Header */}
      <div className="flex items-end justify-between gap-3">
        <div>
          <div className="text-[9px] font-bold uppercase tracking-[.22em] text-[#8a6c43]">
            WHITMORE · TRACKING
          </div>
          <h1 className="mt-1 font-display text-[30px] leading-tight text-[#172641]">
            {t.orders}
          </h1>
          <p className="mt-1 text-[12px] text-[#172641]/65">
            {lang === "ru"
              ? "Статус оплаты, выкупа из Китая и карго-доставки в реальном времени."
              : "To‘lov holati, Xitoydan xarid va kargo yetkazib berish jarayonini kuzating."}
          </p>
        </div>
        <button
          type="button"
          onClick={loadOrders}
          className="rounded-full border border-[#172641]/20 bg-[#fbf8f2] px-3.5 py-2 text-[10px] font-bold uppercase tracking-wider text-[#172641] cursor-pointer transition active:scale-95"
        >
          ↻ {lang === "ru" ? "Обновить" : "Yangilash"}
        </button>
      </div>

      {/* Order Code Lookup Box */}
      <form
        onSubmit={handleLookup}
        className="rounded-2xl border border-[#172641]/15 bg-[#fbf8f2] p-4 shadow-sm space-y-2.5"
      >
        <div className="text-[10px] font-bold uppercase tracking-[.16em] text-[#8a6c43]">
          🔎 {lang === "ru" ? "Проверка заказа по коду" : "Buyurtmani kod orqali tekshirish"}
        </div>
        <div className="flex gap-2">
          <input
            value={lookupCode}
            onChange={(e) => setLookupCode(e.target.value)}
            placeholder={
              lang === "ru"
                ? "Введите код заказа (напр. WM...)"
                : "Buyurtma kodini kiriting (masalan: WM...)"
            }
            className="h-11 flex-1 rounded-xl border border-[#172641]/20 bg-white px-3.5 font-mono text-xs font-bold uppercase text-[#172641] outline-none focus:border-[#172641]"
          />
          <button
            type="submit"
            disabled={searching || !lookupCode.trim()}
            className="h-11 rounded-xl bg-[#172641] px-5 text-[11px] font-bold uppercase tracking-[.12em] text-[#f4efe5] border-0 cursor-pointer disabled:opacity-50"
          >
            {searching
              ? "..."
              : lang === "ru"
              ? "Найти"
              : "Kuzatish"}
          </button>
        </div>
      </form>

      {/* Sartorial Club Loyalty Card */}
      <div className="overflow-hidden rounded-2xl border border-[#d6bd92]/40 bg-gradient-to-br from-[#172641] via-[#1c2e4f] to-[#121c2e] p-5 text-[#f4efe5] shadow-lg relative">
        <div className="absolute right-4 top-4 text-3xl opacity-20 pointer-events-none">⚜️</div>
        <div className="flex items-center justify-between">
          <span className="font-display text-xs tracking-[.22em] text-[#d6bd92]">
            WHITMORE SARTORIAL CLUB
          </span>
          <span className="rounded-full bg-[#d6bd92] px-2.5 py-0.5 text-[9px] font-extrabold uppercase text-[#172641]">
            {orders.length >= 5
              ? "👑 VIP Member"
              : orders.length >= 3
              ? "🥇 Gold Member"
              : orders.length >= 1
              ? "🥈 Silver Member"
              : "Classic Member"}
          </span>
        </div>

        <div className="mt-3.5 flex items-baseline justify-between border-t border-white/10 pt-3">
          <div>
            <div className="text-[9px] font-bold uppercase tracking-wider text-[#d6bd92]">
              Imtiyozlar va Keshbek
            </div>
            <div className="mt-0.5 text-xs text-white/90 font-medium">
              {orders.length >= 5
                ? "Keyingi buyurtmaga 7% keshbek va bepul BTS/EMU pochta"
                : orders.length >= 3
                ? "Keyingi buyurtmaga 5% keshbek va bepul BTS/EMU pochta"
                : orders.length >= 1
                ? "Keyingi buyurtmaga 3% keshbek"
                : "Birinchi buyurtmangizdan so‘ng Silver darajaga o‘tasiz"}
            </div>
          </div>
          <div className="text-right">
            <div className="text-[9px] uppercase tracking-wider text-white/50">
              Buyurtmalar
            </div>
            <div className="font-display text-lg font-bold text-[#d6bd92]">
              {orders.length} ta
            </div>
          </div>
        </div>
      </div>

      {/* Orders List */}
      {loading ? (
        <SkeletonList count={3} />
      ) : orders.length === 0 ? (
        <div className="rounded-2xl border border-[#172641]/15 bg-[#fbf8f2] px-6 py-14 text-center space-y-4">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-[#172641]/10 text-[#172641]">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.7"
            >
              <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z" />
              <path d="m3.3 7 8.7 5 8.7-5" />
              <path d="M12 22V12" />
            </svg>
          </div>
          <div>
            <h2 className="font-display text-[22px] text-[#172641]">
              {lang === "ru" ? "У вас пока нет заказов" : "Sizda hali buyurtmalar yo‘q"}
            </h2>
            <p className="mt-1 text-xs text-[#172641]/60">
              {lang === "ru"
                ? "Выберите классическую одежду из нашего каталога или введите код заказа выше."
                : "Katalogimizdan o‘zingizga mos kiyim tanlang yoki yuqorida buyurtma kodingizni kiriting."}
            </p>
          </div>
          <Link
            to="/miniapp/catalog"
            className="inline-block rounded-full bg-[#172641] px-7 py-3 text-[11px] font-bold uppercase tracking-[.16em] text-[#f4efe5] no-underline"
          >
            {t.catalog} →
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((o) => {
            const step = stepIndex(o.status);
            const pct = Math.min(100, Math.round(((step + 1) / 7) * 100));
            const needsPayment =
              o.status === "new" || o.status === "awaiting_payment";

            return (
              <Link
                key={o.code}
                to={`/miniapp/order/${o.code}`}
                state={{ order: o }}
                className="block overflow-hidden rounded-2xl border border-[#172641]/15 bg-[#fbf8f2] text-[#172641] no-underline shadow-sm transition hover:-translate-y-0.5 hover:border-[#172641]/40 hover:shadow-md"
              >
                {/* Card Top Header */}
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#172641]/10 bg-[#172641] px-4 py-3 text-[#f4efe5]">
                  <div className="flex items-center gap-2.5">
                    <span className="font-mono text-xs font-extrabold tracking-wider text-[#d6bd92]">
                      #{o.code}
                    </span>
                    <span className="text-[11px] text-[#f4efe5]/65">
                      · {o.created_at}
                    </span>
                  </div>
                  <StatusBadge status={o.status} />
                </div>

                {/* Card Body */}
                <div className="p-4 space-y-3.5">
                  {/* Cargo Progress Bar */}
                  {o.status !== "cancelled" && (
                    <div className="space-y-1.5">
                      <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-wider text-[#8a6c43]">
                        <span>
                          {lang === "ru"
                            ? `Этап доставки: ${step + 1} из 7`
                            : `Jarayon bosqichi: 7 dan ${step + 1}-bosqich`}
                        </span>
                        <span>{pct}%</span>
                      </div>
                      <div className="h-2 w-full overflow-hidden rounded-full bg-[#e6dccb]">
                        <div
                          className="h-full rounded-full bg-gradient-to-r from-[#172641] to-[#b5915f] transition-all duration-500"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                      {o.tracking && (
                        <div className="pt-1 text-[11px] font-semibold text-[#172641]">
                          🚚 Trek-kod:{" "}
                          <span className="font-mono font-bold text-[#8a6c43]">
                            {o.tracking}
                          </span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Items Snapshot */}
                  <div className="space-y-1 border-t border-[#172641]/10 pt-2.5">
                    {(o.items || []).map((it: any, idx: number) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between gap-2 text-xs"
                      >
                        <span className="truncate font-semibold text-[#172641]">
                          {it.name}{" "}
                          <span className="font-normal text-[#172641]/65">
                            ({it.size}
                            {it.color ? ` · ${it.color}` : ""}) × {it.qty}
                          </span>
                        </span>
                        <span className="shrink-0 font-semibold text-[#172641]/80">
                          {formatPrice(it.price * it.qty)}
                        </span>
                      </div>
                    ))}
                  </div>

                  {/* Price & Payment Status Footer */}
                  <div className="flex flex-wrap items-center justify-between gap-2 border-t border-[#172641]/10 pt-3">
                    <div>
                      <div className="text-[10px] uppercase tracking-wider text-[#172641]/55">
                        {lang === "ru" ? "Итоговая сумма" : "Jami buyurtma"}
                      </div>
                      <div className="font-display text-[20px] font-semibold text-[#172641]">
                        {formatPrice(o.total)}
                      </div>
                      {o.paid_amount > 0 ? (
                        <div className="text-[11px] font-bold text-[#2b6cb0]">
                          ✓ {lang === "ru" ? "Оплачено: " : "To‘langan: "}
                          {formatPrice(o.paid_amount)}
                        </div>
                      ) : needsPayment ? (
                        <div className="text-[11px] font-bold text-[#a8742a]">
                          ⏳{" "}
                          {o.receipt_photo
                            ? lang === "ru"
                              ? "Чек на проверке у админа"
                              : "Chek admin tekshiruvida"
                            : lang === "ru"
                            ? `К предоплате (${o.advance_pct || 30}%): ${formatPrice(
                                o.advance_amount || Math.round(o.total * 0.3)
                              )}`
                            : `Avans to‘lov (${o.advance_pct || 30}%): ${formatPrice(
                                o.advance_amount || Math.round(o.total * 0.3)
                              )}`}
                        </div>
                      ) : null}
                    </div>

                    <span className="inline-flex items-center gap-1.5 rounded-full bg-[#172641] px-4 py-2 text-[10px] font-bold uppercase tracking-[.12em] text-[#f4efe5]">
                      <span>
                        {needsPayment && !o.receipt_photo
                          ? lang === "ru"
                            ? "💳 Оплатить / Детали"
                            : "💳 To‘lov va Batafsil"
                          : lang === "ru"
                          ? "Отследить заказ"
                          : "Batafsil kuzatish"}
                      </span>
                      <span>→</span>
                    </span>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}

      {/* Direct Support Banner */}
      {contactUser && (
        <a
          href={`https://t.me/${contactUser}`}
          target="_blank"
          rel="noreferrer"
          className="flex items-center justify-between rounded-2xl border border-[#172641]/15 bg-[#172641] px-5 py-4 text-[#f4efe5] no-underline"
        >
          <div>
            <div className="text-[9px] font-bold uppercase tracking-[.2em] text-[#d6bd92]">
              {lang === "ru" ? "ЕСТЬ ВОПРОСЫ ПО ЗАКАЗУ?" : "BUYURTMA BO‘YICHA SAVOLINGIZ BORMI?"}
            </div>
            <div className="mt-1 text-xs font-semibold">
              {lang === "ru"
                ? `Написать менеджеру @${contactUser}`
                : `Menejer bilan bog‘lanish (@${contactUser})`}
            </div>
          </div>
          <span className="text-lg text-[#d6bd92]">→</span>
        </a>
      )}
    </div>
  );
}

// ---------------- ABOUT SCREEN (REPLIT EDITORIAL) ----------------
function AboutScreen({
  content,
  lang,
  favIds,
  onToggleFav,
}: {
  content: any;
  lang: string;
  favIds: number[];
  onToggleFav: (id: number) => void;
}) {
  const { t } = useLang();
  const [myOrders, setMyOrders] = useState<any[]>([]);
  const [favProducts, setFavProducts] = useState<any[]>([]);
  const [openFaq, setOpenFaq] = useState<number | null>(0);

  useEffect(() => {
    shopFetch("/api/shop/orders")
      .then((res) => setMyOrders(res))
      .catch(() => {});
    shopFetch("/api/shop/favorites")
      .then((res) => setFavProducts(res.products || []))
      .catch(() => {});
  }, [favIds.length]);

  const about = lang === "ru" ? content?.about_ru : content?.about_uz;
  const delivery = lang === "ru" ? content?.delivery_ru : content?.delivery_uz;
  const returns = lang === "ru" ? content?.returns_ru : content?.returns_uz;
  const faq = content?.faq || [];
  const contactUser = content?.contact_username?.replace(/^@/, "");

  return (
    <div className="mx-auto max-w-3xl px-4 pt-6 space-y-8 rise-in">
      {/* Brand Story */}
      <div>
        <img
          src="/whitmore-logo.jpg"
          alt="Whitmore"
          onError={(e) => {
            (e.currentTarget as HTMLImageElement).style.display = "none";
          }}
          className="h-16 w-16 rounded-full object-cover border border-[#172641]/20"
        />
        <h1 className="mt-4 font-display text-[32px] text-[#172641]">
          {t.about}
        </h1>
        <p className="mt-3 whitespace-pre-line text-[13px] leading-6 text-[#172641]/80">
          {about}
        </p>

        {contactUser && (
          <a
            href={`https://t.me/${contactUser}`}
            target="_blank"
            rel="noreferrer"
            className="mt-5 flex w-full items-center justify-between bg-[#172641] px-5 py-4 text-left text-[#f4efe5] no-underline"
          >
            <span>
              <span className="block text-[9px] font-bold uppercase tracking-[.2em] text-[#d6bd92]">
                {t.contacts}
              </span>
              <span className="mt-1 block text-[14px] font-semibold">
                @{contactUser}
              </span>
            </span>
            <span>→</span>
          </a>
        )}
      </div>

      {/* Customer Orders */}
      {myOrders.length > 0 && (
        <section className="border-t border-[#172641]/15 pt-5 space-y-3">
          <h2 className="font-display text-[22px] text-[#172641]">
            {t.orders}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {myOrders.map((o) => (
              <Link
                key={o.code}
                to={`/miniapp/order/${o.code}`}
                className="flex items-center justify-between border border-[#172641]/15 bg-[#fbf8f2] p-3.5 text-[#172641] no-underline hover:border-[#172641]"
              >
                <div>
                  <div className="font-bold text-sm">{o.code}</div>
                  <div className="text-xs text-[#8a6c43] font-semibold mt-0.5">
                    {formatPrice(o.total)}
                  </div>
                </div>
                <StatusBadge status={o.status} />
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Favorites */}
      {favProducts.length > 0 && (
        <section className="border-t border-[#172641]/15 pt-5 space-y-3">
          <h2 className="font-display text-[22px] text-[#172641]">
            {t.favorites}
          </h2>
          <div className="miniapp-product-grid">
            {favProducts.map((p) => (
              <ProductCard
                key={p.id}
                p={p}
                isFav={favIds.includes(p.id)}
                onToggleFav={onToggleFav}
              />
            ))}
          </div>
        </section>
      )}

      {/* Delivery & Return Rules */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 border-t border-[#172641]/15 pt-5">
        <div>
          <h2 className="text-[10px] font-bold uppercase tracking-[.2em] text-[#8a6c43]">
            {t.deliveryRules}
          </h2>
          <p className="mt-2 whitespace-pre-line text-[13px] leading-6 text-[#172641]/80">
            {delivery}
          </p>
        </div>
        <div>
          <h2 className="text-[10px] font-bold uppercase tracking-[.2em] text-[#8a6c43]">
            {t.returnRules}
          </h2>
          <p className="mt-2 whitespace-pre-line text-[13px] leading-6 text-[#172641]/80">
            {returns}
          </p>
        </div>
      </div>

      {/* FAQ Accordion */}
      {faq.length > 0 && (
        <section className="border-t border-[#172641]/15 pt-5">
          <h2 className="font-display text-[22px] text-[#172641]">
            {t.faqTitle}
          </h2>
          <div className="mt-3 divide-y divide-[#172641]/12 border-y border-[#172641]/12">
            {faq.map((item: any, i: number) => {
              const isOpen = openFaq === i;
              return (
                <div key={i}>
                  <button
                    type="button"
                    onClick={() => setOpenFaq(isOpen ? null : i)}
                    className="flex w-full items-center justify-between gap-3 py-4 text-left text-[13px] font-semibold text-[#172641] bg-transparent border-0 cursor-pointer"
                  >
                    <span>
                      {lang === "ru" ? item.q_ru || item.q_uz : item.q_uz}
                    </span>
                    <span className="text-sm">{isOpen ? "−" : "+"}</span>
                  </button>
                  {isOpen && (
                    <p className="pb-4 text-[12.5px] leading-6 text-[#172641]/75">
                      {lang === "ru" ? item.a_ru || item.a_uz : item.a_uz}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      )}
    </div>
  );
}
