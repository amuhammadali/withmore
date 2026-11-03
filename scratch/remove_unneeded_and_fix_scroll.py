import os
import re

print("Starting cleanup of 3 cards & fitting passport and fixing scrollbar...")

# 1. Fix scrollbar in index.css
css_path = "frontend/src/index.css"
with open(css_path, "r", encoding="utf-8") as f:
    css = f.read()

no_scroll_css = """
/* Hide scrollbars across the entire app */
html, body, #root, * {
  scrollbar-width: none !important;
  -ms-overflow-style: none !important;
}
*::-webkit-scrollbar, html::-webkit-scrollbar, body::-webkit-scrollbar {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
}
"""

if "Hide scrollbars across the entire app" not in css:
    css = no_scroll_css + "\n" + css
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css)
    print("index.css updated with no-scrollbar rules!")

# 2. Update MiniApp.tsx
miniapp_path = "frontend/src/miniapp/MiniApp.tsx"
with open(miniapp_path, "r", encoding="utf-8") as f:
    app = f.read()

# 2a. Remove 3 highlight cards (Aniq Bichim, 100% Original, Tezkor Kuryer)
highlight_pattern = r'\{\/\* Atelier Excellence Highlights \*\/\}[\s\S]*?<\/section>'
if re.search(highlight_pattern, app):
    app = re.sub(highlight_pattern, '', app, count=1)
    print("Removed 3 highlight cards from Home Screen!")

# 2b. Remove Fitting Button and Modal from ProductScreen
fitting_btn_pattern = r'\{\/\* Atelier Bespoke Fitting Button \*\/\}[\s\S]*?\{\/\* 1-Click Quick Order Button \*\/\}'
if re.search(fitting_btn_pattern, app):
    app = re.sub(fitting_btn_pattern, '{/* 1-Click Quick Order Button */}', app, count=1)
    print("Removed Fitting button from ProductScreen!")

fitting_modal_pattern = r'\{\/\* Atelier Fitting Appointment Modal \*\/\}[\s\S]*?\{\/\* Quick Order Modal \*\/\}'
if re.search(fitting_modal_pattern, app):
    app = re.sub(fitting_modal_pattern, '{/* Quick Order Modal */}', app, count=1)
    print("Removed Fitting modal from ProductScreen!")

# 2c. Remove Qomat Pasporti and Fittings sections from AboutScreen
passport_pattern = r'\{\/\* ---------------- BESPOKE QOMAT PASPORTI \(SARTORIAL PROFILE\) ---------------- \*\/\}[\s\S]*?\{\/\* Customer Orders \*\/\}'
if re.search(passport_pattern, app):
    app = re.sub(passport_pattern, '{/* Customer Orders */}', app, count=1)
    print("Removed Qomat Pasporti & Primerkalar from AboutScreen!")

with open(miniapp_path, "w", encoding="utf-8") as f:
    f.write(app)
print("MiniApp.tsx cleanup complete!")

# 3. Update AdminCrmPage.tsx: remove fittings tab
crm_path = "frontend/src/admin/AdminCrmPage.tsx"
with open(crm_path, "r", encoding="utf-8") as f:
    crm = f.read()

# Revert activeTab to pipeline | tasks
crm = crm.replace('<"pipeline" | "tasks" | "fittings">', '<"pipeline" | "tasks">')

# Remove fittings button in header
fittings_btn_code = '''              <button
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
if fittings_btn_code in crm:
    crm = crm.replace(fittings_btn_code, "")
    print("Removed fittings tab button in AdminCrmPage.tsx!")

# Remove fittings panel
fittings_panel_pattern = r'\{\/\* ---------------- 2\.5 ATELIER FITTINGS & BESPOKE CALENDAR ---------------- \*\/\}[\s\S]*?\{\/\* ---------------- 3\. CUSTOMER 360° SARTORIAL DOSSIER MODAL ---------------- \*\/\}'
if re.search(fittings_panel_pattern, crm):
    crm = re.sub(fittings_panel_pattern, '{/* ---------------- 3. CUSTOMER 360° SARTORIAL DOSSIER MODAL ---------------- */}', crm, count=1)
    print("Removed fittings panel in AdminCrmPage.tsx!")

with open(crm_path, "w", encoding="utf-8") as f:
    f.write(crm)
print("AdminCrmPage.tsx cleanup complete!")

