import os

file_path = r"c:\Users\muham\OneDrive\Desktop\withmore\frontend\src\miniapp\MiniApp.tsx"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Catalog search input & buttons
content = content.replace(
    'border border-[#dccab0] bg-white/95 pl-10 pr-4 text-[13px] text-slate-900 placeholder-[#172641]/40 shadow-[0_2px_8px_rgba(23,38,65,0.03)] outline-none transition-all duration-200 focus:border-[#c5a676] focus:ring-2 focus:ring-[#c5a676]/30 focus:shadow-[0_4px_16px_rgba(197,166,118,0.18)]',
    'border border-slate-200 bg-white pl-10 pr-4 text-[13px] text-slate-900 placeholder-slate-400 shadow-[0_1px_3px_rgba(0,0,0,0.03)] outline-none transition-all duration-200 focus:border-slate-900 focus:ring-2 focus:ring-slate-900/10'
)
content = content.replace(
    'border-[#dccab0] bg-white/95 text-slate-900 shadow-[0_2px_8px_rgba(23,38,65,0.03)] hover:border-[#c5a676] hover:bg-white hover:text-[#0b1728] hover:shadow-[0_4px_16px_rgba(197,166,118,0.22)] hover:-translate-y-0.5',
    'border-slate-200 bg-white text-slate-800 shadow-xs hover:border-slate-300 hover:text-black active:scale-95'
)
content = content.replace(
    'border-[#dccab0] bg-white/95 text-slate-900 shadow-[0_2px_8px_rgba(23,38,65,0.03)] hover:border-[#c5a676] hover:bg-white hover:text-[#a3463c] hover:shadow-[0_4px_16px_rgba(163,70,60,0.18)] hover:-translate-y-0.5',
    'border-slate-200 bg-white text-slate-800 shadow-xs hover:border-slate-300 hover:text-rose-600 active:scale-95'
)

# 2. Filter drawer
content = content.replace(
    'rounded-2xl border border-[#dccab0] bg-white/95 p-3.5 shadow-sm',
    'rounded-2xl border border-slate-200 bg-white p-3.5 shadow-sm'
)
content = content.replace(
    'rounded-xl border border-[#dccab0] bg-[#faf7f2] px-2.5 text-[12px] font-medium normal-case tracking-normal text-slate-900 outline-none focus:border-[#c5a676]',
    'rounded-xl border border-slate-200 bg-slate-50 px-2.5 text-[12px] font-medium normal-case tracking-normal text-slate-900 outline-none focus:border-slate-900'
)

# 3. Category pills in CatalogScreen
content = content.replace(
    'bg-gradient-to-r from-[#172641] via-[#223558] to-[#121c2e] text-[#faf7f2] shadow-[0_4px_16px_rgba(23,38,65,0.28)] ring-2 ring-[#c5a676] ring-offset-2 ring-offset-[#f6f2ea] scale-[1.02]',
    'bg-slate-900 text-white shadow-sm ring-1 ring-slate-900 scale-[1.02]'
)
content = content.replace(
    'border border-[#dccab0] bg-gradient-to-b from-white to-[#fbf7f0] text-slate-900 shadow-[0_2px_8px_rgba(23,38,65,0.04)] hover:border-[#c5a676] hover:shadow-[0_6px_20px_rgba(197,166,118,0.28)] hover:-translate-y-0.5 hover:text-[#0b1728] active:scale-95',
    'border border-slate-200/90 bg-white text-slate-800 shadow-xs hover:border-slate-300 hover:shadow-md hover:-translate-y-0.5 hover:text-black active:scale-95'
)

# 4. ProductScreen gallery bg
content = content.replace(
    'relative aspect-[3/4] max-h-[560px] w-full overflow-hidden bg-[#e6dccb] select-none',
    'relative aspect-[3/4] max-h-[560px] w-full overflow-hidden bg-[#F1F3F7] select-none'
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("CatalogScreen & ProductScreen updated successfully!")

