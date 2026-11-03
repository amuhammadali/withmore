import os

miniapp_path = r"c:\Users\muham\OneDrive\Desktop\withmore\frontend\src\miniapp\MiniApp.tsx"
admin_path = r"c:\Users\muham\OneDrive\Desktop\withmore\frontend\src\admin\AdminPages.tsx"

# 1. Update MiniApp.tsx
with open(miniapp_path, "r", encoding="utf-8") as f:
    miniapp_content = f.read()

# Make getCategoryIcon return empty string
old_fn = """function getCategoryIcon(name: string): string {
  const n = (name || "").toLowerCase();
  if (n.includes("kostyum") || n.includes("smoking") || n.includes("костюм") || n.includes("пиджак")) return "👔";
  if (n.includes("ko'ylak") || n.includes("koylak") || n.includes("rubashka") || n.includes("рубашк")) return "👔";
  if (n.includes("poyabzal") || n.includes("tufli") || n.includes("oyoq") || n.includes("обув") || n.includes("туфли") || n.includes("krossovk")) return "👞";
  if (n.includes("shim") || n.includes("bryuk") || n.includes("брюк") || n.includes("джинс")) return "👖";
  if (n.includes("kurtka") || n.includes("palto") || n.includes("nimcha") || n.includes("куртк") || n.includes("пальто")) return "🧥";
  if (n.includes("aksessuar") || n.includes("galstuk") || n.includes("kamar") || n.includes("аксессуар")) return "🎒";
  return "✨";
}"""

new_fn = """function getCategoryIcon(name: string): string {
  return "";
}"""

if old_fn in miniapp_content:
    miniapp_content = miniapp_content.replace(old_fn, new_fn)
    print("getCategoryIcon in MiniApp set to empty!")
else:
    print("getCategoryIcon exact string not found in MiniApp, replacing via search...")

# Replace CatalogScreen category pill strip
catalog_marker_start = "{/* Category Pill Strip"
catalog_marker_end = '<div className="mb-4 mt-2.5 text-[10px]'

start_c = miniapp_content.find(catalog_marker_start)
end_c = miniapp_content.find(catalog_marker_end)

if start_c != -1 and end_c != -1:
    new_catalog_strip = """{/* Category Pill Strip (Pure Typography, No Icons) */}
      <div className="no-scrollbar -mx-4 mt-3 flex items-center gap-2 overflow-x-auto px-4 pb-2">
        <button
          type="button"
          onClick={() => setSearchParams({})}
          className={`shrink-0 inline-flex items-center rounded-2xl px-4 py-2 text-[11.5px] font-bold tracking-wide transition-all duration-200 cursor-pointer ${
            !selectedCat
              ? "bg-[#172641] text-white shadow-sm ring-1 ring-[#172641] scale-[1.02]"
              : "border border-slate-200/90 bg-white text-[#172641] shadow-xs hover:border-[#172641]/40 hover:shadow-md hover:-translate-y-0.5 active:scale-95"
          }`}
        >
          <span>{t.allCategories}</span>
        </button>
        {categories.map((c) => {
          const active = selectedCat === c.id;
          const label = lang === "ru" ? c.name_ru || c.name_uz : c.name_uz;
          return (
            <button
              key={c.id}
              type="button"
              onClick={() => setSearchParams({ category: String(c.id) })}
              className={`shrink-0 inline-flex items-center rounded-2xl px-4 py-2 text-[11.5px] font-bold tracking-wide transition-all duration-200 cursor-pointer ${
                active
                  ? "bg-[#172641] text-white shadow-sm ring-1 ring-[#172641] scale-[1.02]"
                  : "border border-slate-200/90 bg-white text-[#172641] shadow-xs hover:border-[#172641]/40 hover:shadow-md hover:-translate-y-0.5 active:scale-95"
              }`}
            >
              <span>{label}</span>
            </button>
          );
        })}
      </div>

      """
    miniapp_content = miniapp_content[:start_c] + new_catalog_strip + miniapp_content[end_c:]
    print("CatalogScreen category pills replaced without icons!")
else:
    print(f"Catalog markers not found: {start_c}, {end_c}")

with open(miniapp_path, "w", encoding="utf-8") as f:
    f.write(miniapp_content)


# 2. Update AdminPages.tsx
with open(admin_path, "r", encoding="utf-8") as f:
    admin_content = f.read()

# Make getCategoryIcon in AdminPages return empty string
old_admin_fn = """export function getCategoryIcon(name: string = ""): string {
  const n = (name || "").toLowerCase();
  if (n.includes("kostyum") || n.includes("ko'ylak") || n.includes("rubashka") || n.includes("shirt") || n.includes("suit")) return "👔";
  if (n.includes("poyabzal") || n.includes("tufli") || n.includes("krossovk") || n.includes("shoes") || n.includes("boot") || n.includes("oyoq")) return "👞";
  if (n.includes("shim") || n.includes("jeans") || n.includes("pants") || n.includes("trousers") || n.includes("bryuk")) return "👖";
  if (n.includes("kurtka") || n.includes("palto") || n.includes("jaket") || n.includes("outerwear") || n.includes("coat")) return "🧥";
  if (n.includes("sumka") || n.includes("aksessuar") || n.includes("kamar") || n.includes("bag") || n.includes("accessories")) return "🎒";
  if (n.includes("soat") || n.includes("watch")) return "⌚";
  if (n.includes("sport") || n.includes("fitnes")) return "🏃";
  return "🏷️";
}"""

new_admin_fn = """export function getCategoryIcon(name: string = ""): string {
  return "";
}"""

if old_admin_fn in admin_content:
    admin_content = admin_content.replace(old_admin_fn, new_admin_fn)
    print("getCategoryIcon in AdminPages set to empty!")

# In Admin filter buttons:
admin_content = admin_content.replace(
    'const icon = c.id ? getCategoryIcon(c.name_uz) : "✨";',
    'const icon = "";'
)
admin_content = admin_content.replace(
    '<span>{icon}</span>\n              <span>{c.name_uz}</span>',
    '<span>{c.name_uz}</span>'
)
admin_content = admin_content.replace(
    '<span>{icon}</span>\r\n              <span>{c.name_uz}</span>',
    '<span>{c.name_uz}</span>'
)

# In Category card:
admin_content = admin_content.replace(
    '<span className="text-base">{getCategoryIcon(nameUz)}</span>',
    ''
)
admin_content = admin_content.replace(
    '<span className="text-xl">{getCategoryIcon(editItem.name_uz)}</span>',
    ''
)

# Category card icon box -> clean index box
old_cat_icon_box = """<div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-[#172641]/10 via-[#172641]/5 to-[#c5a776]/15 text-2xl border border-[#172641]/10 shadow-xs transition-transform duration-300 group-hover:scale-105">
                        {icon}
                      </div>"""

new_cat_icon_box = """<div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#172641]/10 text-[12px] font-black text-[#172641] border border-[#172641]/10">
                        #{idx + 1}
                      </div>"""

admin_content = admin_content.replace(old_cat_icon_box, new_cat_icon_box)

with open(admin_path, "w", encoding="utf-8") as f:
    f.write(admin_content)

print("AdminPages.tsx category icons completely removed!")

