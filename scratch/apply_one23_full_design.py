import re

file_path = r"frontend/src/miniapp/MiniApp.tsx"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# ----------------- 1. PRODUCT CARD (ONE23 1:1 DESIGN) -----------------
old_product_card = """function ProductCard({
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
    <div className="group relative min-w-0 self-start rise-in rounded-3xl border border-slate-200/80 bg-white p-2.5 shadow-[0_4px_20px_-4px_rgba(0,0,0,0.05)] transition-all duration-300 hover:-translate-y-1 hover:border-slate-300 hover:shadow-[0_16px_36px_-6px_rgba(15,23,42,0.12)]">
      <Link
        to={`/miniapp/product/${p.id}`}
        className="block w-full min-w-0 text-left no-underline text-slate-900"
      >
        <div className="relative aspect-[3/4] overflow-hidden rounded-[20px] bg-[#F1F3F7]">
          <ProductImage
            src={p.thumb}
            alt={name}
            className="h-full w-full object-cover transition-transform duration-700 ease-out group-hover:scale-106"
          />

          {/* Top-left Sale Type Badge */}
          <div className="absolute left-2.5 top-2.5 flex items-center gap-1.5 rounded-full bg-white/92 backdrop-blur-md px-2.5 py-1 text-[9px] font-bold uppercase tracking-wider text-slate-800 shadow-xs border border-white/70">
            <span className={`h-1.5 w-1.5 rounded-full ${isStock ? "bg-emerald-500 animate-pulse" : "bg-amber-500"}`} />
            <span>{isStock ? t.inStockBadge : t.preorderBadge}</span>
          </div>

          {/* Sold out bottom bar */}
          {p.sold_out && (
            <div className="absolute inset-0 flex items-center justify-center bg-slate-950/60 backdrop-blur-[2px]">
              <span className="rounded-full bg-white px-3 py-1 text-[10px] font-extrabold uppercase tracking-widest text-slate-900 shadow-md">
                {t.soldOut}
              </span>
            </div>
          )}
        </div>

        <div className="mt-2.5 px-1">
          <div className="text-[9px] font-bold tracking-[0.16em] uppercase text-slate-400 truncate">
            WITHMORE BESPOKE
          </div>
          <div className="font-display text-[14px] sm:text-[15px] font-semibold text-slate-900 line-clamp-1 group-hover:text-[#8a6c43] transition-colors mt-0.5">
            {name}
          </div>
          <div className="mt-2 flex items-center justify-between gap-1 pt-1.5 border-t border-slate-100">
            <div className="flex flex-col">
              <span className="text-[8.5px] uppercase tracking-wider font-semibold text-slate-400">Narx</span>
              <span className="text-[13px] sm:text-[14px] font-black text-[#172641] tracking-tight leading-none">
                {formatPrice(p.price)}
              </span>
            </div>
            <span className="inline-flex items-center gap-1 rounded-full bg-[#172641] px-3.5 py-1.5 text-[10px] font-bold text-white shadow-xs transition-all duration-200 group-hover:bg-[#223558] group-hover:scale-105 active:scale-95">
              <span>Tanlash</span>
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </span>
          </div>
        </div>
      </Link>

      {/* Top-right Favorite Heart Button */}
      <button
        type="button"
        aria-label={t.favorites}
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          onToggleFav(p.id);
        }}
        className="absolute top-4 right-4 flex h-8 w-8 items-center justify-center rounded-full bg-white/90 text-slate-700 shadow-xs backdrop-blur-md transition-all duration-200 hover:scale-110 hover:text-[#a3463c] active:scale-90 cursor-pointer border border-white/60"
      >
        <svg
          width="15"
          height="15"
          viewBox="0 0 24 24"
          fill={isFav ? "#a3463c" : "none"}
          stroke={isFav ? "#a3463c" : "currentColor"}
          strokeWidth="2"
        >
          <path d="M12 21s-7-4.5-9.5-9A5.5 5.5 0 0 1 12 6a5.5 5.5 0 0 1 9.5 6c-2.5 4.5-9.5 9-9.5 9z" />
        </svg>
      </button>
    </div>
  );
}"""

new_product_card = """function ProductCard({
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
    <div className="group relative min-w-0 self-start rise-in rounded-2xl border border-slate-200/90 bg-white overflow-hidden shadow-2xs transition-all duration-200 hover:border-slate-300 hover:shadow-md flex flex-col w-full">
      <Link
        to={`/miniapp/product/${p.id}`}
        className="block w-full min-w-0 text-left no-underline text-slate-900"
      >
        {/* ONE23 Aspect Ratio 5/6 Image Box */}
        <div className="relative aspect-[5/6] w-full overflow-hidden bg-[#F2F4F8]">
          <ProductImage
            src={p.thumb}
            alt={name}
            className="h-full w-full object-cover transition-transform duration-500 ease-out group-hover:scale-104"
          />

          {/* Top-left ONE23 Badge */}
          <div className="absolute left-2 top-2 flex items-center gap-1 rounded-md bg-white/95 backdrop-blur-xs px-2 py-0.5 text-[9.5px] font-bold uppercase tracking-wider text-slate-800 shadow-2xs border border-white/80">
            <span className={`h-1.5 w-1.5 rounded-full ${isStock ? "bg-emerald-500" : "bg-amber-500"}`} />
            <span>{isStock ? (lang === "ru" ? "В наличии" : "Mavjud") : (lang === "ru" ? "Предзаказ" : "Buyurtmaga")}</span>
          </div>

          {/* Sold out overlay */}
          {p.sold_out && (
            <div className="absolute inset-0 flex items-center justify-center bg-slate-950/60 backdrop-blur-2xs">
              <span className="rounded-md bg-white px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-900 shadow-sm">
                {t.soldOut}
              </span>
            </div>
          )}
        </div>

        {/* ONE23 Card Body */}
        <div className="p-2 sm:p-2.5 flex flex-col flex-1 gap-1">
          <h3 className="text-xs sm:text-[13px] font-medium text-slate-900 line-clamp-2 leading-snug group-hover:text-[#172641]">
            {name}
          </h3>

          <div className="mt-0.5 text-[13px] sm:text-sm font-bold text-slate-900 tabular-nums">
            {formatPrice(p.price)}
          </div>

          <div className="mt-auto pt-1.5">
            <span className="w-full h-8 sm:h-8.5 rounded-xl bg-[#172641] hover:bg-[#223558] text-white text-[11px] font-semibold flex items-center justify-center gap-1.5 transition active:scale-95 shadow-2xs">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="9" cy="20" r="1.5" />
                <circle cx="18" cy="20" r="1.5" />
                <path d="M3 4h2l2.5 12h12l2-8H6" />
              </svg>
              <span>{lang === "ru" ? "В корзину" : "Savatga"}</span>
            </span>
          </div>
        </div>
      </Link>

      {/* Top-right ONE23 Floating Favorite Button */}
      <button
        type="button"
        aria-label={t.favorites}
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          onToggleFav(p.id);
        }}
        className="absolute top-2 right-2 flex h-7.5 w-7.5 items-center justify-center rounded-full bg-white/90 text-slate-600 shadow-xs backdrop-blur-xs transition hover:scale-110 hover:text-[#a3463c] active:scale-90 cursor-pointer border border-white/70"
      >
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill={isFav ? "#a3463c" : "none"}
          stroke={isFav ? "#a3463c" : "currentColor"}
          strokeWidth="2"
        >
          <path d="M12 21s-7-4.5-9.5-9A5.5 5.5 0 0 1 12 6a5.5 5.5 0 0 1 9.5 6c-2.5 4.5-9.5 9-9.5 9z" />
        </svg>
      </button>
    </div>
  );
}"""

if old_product_card in code:
    code = code.replace(old_product_card, new_product_card, 1)
    print("Replaced ProductCard with ONE23 1:1 Design!")

# ----------------- 2. BOTTOM NAVIGATION BAR (ONE23 1:1 FULL-WIDTH) -----------------
old_bottom_nav = """      {/* Floating Creative Capsule Bottom Navigation Bar */}
      <nav
        aria-label="Do‘kon bo‘limlari"
        className="fixed bottom-3 left-0 right-0 z-30 px-2.5 sm:bottom-4 sm:px-5 pointer-events-none"
      >
        <div className="pointer-events-auto mx-auto grid max-w-[600px] grid-cols-5 items-center gap-1 rounded-full border border-white/10 bg-[#0F172A]/92 p-1.5 text-slate-300 shadow-[0_20px_45px_rgba(0,0,0,0.35)] backdrop-blur-2xl">
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
      </nav>"""

new_bottom_nav = """      {/* ONE23 Native Full-Width Bottom Tab Bar */}
      <nav
        aria-label="Do‘kon bo‘limlari"
        className="fixed bottom-0 inset-x-0 z-40 bg-white/95 backdrop-blur-md border-t border-slate-200/90 shadow-[0_-4px_20px_rgba(0,0,0,0.04)]"
      >
        <div className="mx-auto grid max-w-lg grid-cols-4 h-14 items-center px-1">
          <NavTab to="/miniapp" exact label={lang === "ru" ? "Главная" : "Bosh sahifa"} icon="home" />
          <NavTab
            to="/miniapp/catalog"
            label={lang === "ru" ? "Каталог" : "Katalog"}
            alsoMatch="/miniapp/product"
            icon="catalog"
          />
          <NavTab
            to="/miniapp/cart"
            label={lang === "ru" ? "Корзина" : "Savat"}
            badge={cartCount > 0 ? cartCount : undefined}
            icon="cart"
          />
          <NavTab
            to="/miniapp/about"
            label={lang === "ru" ? "Профиль" : "Profil"}
            icon="about"
          />
        </div>
      </nav>"""

if old_bottom_nav in code:
    code = code.replace(old_bottom_nav, new_bottom_nav, 1)
    print("Replaced Floating Nav with ONE23 Native Bottom Tab Bar!")

# ----------------- 3. NAVTAB COMPONENT (ONE23 CLEAN ICONS & LABELS) -----------------
old_navtab = """function NavTab({
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
          ? "bg-gradient-to-b from-[#e5d2ae] to-[#c5a676] text-[#0F172A] font-bold shadow-[0_4px_16px_rgba(197,166,118,0.4)]"
          : "text-slate-400 hover:bg-white/10 hover:text-white"
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
                ? "bg-slate-900 text-white shadow-xs"
                : "bg-[#c5a676] text-[#0F172A]"
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
}"""

new_navtab = """function NavTab({
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
      className={`relative flex h-full flex-col items-center justify-center gap-1 no-underline transition-colors active:scale-95 ${
        active ? "text-[#172641]" : "text-slate-400 hover:text-slate-700"
      }`}
    >
      <div className="relative flex items-center justify-center">
        {icon === "home" && (
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill={active ? "currentColor" : "none"}
            stroke="currentColor"
            strokeWidth={active ? "2" : "1.8"}
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M3 10.5L12 3l9 7.5V20a1 1 0 0 1-1 1h-5.5v-6h-5v6H4a1 1 0 0 1-1-1v-9.5z" />
          </svg>
        )}
        {icon === "catalog" && (
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={active ? "2.2" : "1.8"}
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <rect x="3" y="3" width="7" height="7" rx="1.5" />
            <rect x="14" y="3" width="7" height="7" rx="1.5" />
            <rect x="14" y="14" width="7" height="7" rx="1.5" />
            <rect x="3" y="14" width="7" height="7" rx="1.5" />
          </svg>
        )}
        {icon === "cart" && (
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={active ? "2.2" : "1.8"}
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z" />
            <line x1="3" y1="6" x2="21" y2="6" />
            <path d="M16 10a4 4 0 0 1-8 0" />
          </svg>
        )}
        {icon === "about" && (
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={active ? "2.2" : "1.8"}
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
        )}
        {badge !== undefined && (
          <span className="absolute -right-2.5 -top-1.5 flex h-4 min-w-[16px] items-center justify-center rounded-full bg-[#172641] text-white px-1 text-[9px] font-bold leading-none shadow-xs">
            {badge}
          </span>
        )}
      </div>
      <span className={`text-[10px] tracking-tight ${active ? "font-bold text-[#172641]" : "font-medium text-slate-400"}`}>
        {label}
      </span>
    </Link>
  );
}"""

if old_navtab in code:
    code = code.replace(old_navtab, new_navtab, 1)
    print("Replaced NavTab with ONE23 Clean Icons & Typography!")

# ----------------- 4. MAIN CONTAINER PADDING (pb-20 so bottom bar never covers) -----------------
old_main = '<main className="flex-1">'
new_main = '<main className="flex-1 pb-20">'
if old_main in code:
    code = code.replace(old_main, new_main, 1)
    print("Added pb-20 to main container!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("All ONE23 design transformations completed successfully!")

