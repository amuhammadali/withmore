file_path = r"frontend/src/miniapp/MiniApp.tsx"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

old_lookbook_aspect = 'aspect-[3/4] overflow-hidden rounded-[20px] bg-[#F1F3F7]'
new_lookbook_aspect = 'aspect-[5/6] overflow-hidden bg-[#F2F4F8]'

old_lookbook_container = 'className="group relative min-w-0 self-start rise-in rounded-3xl border border-slate-200/80 bg-white p-2.5 shadow-[0_4px_20px_-4px_rgba(0,0,0,0.05)] transition-all duration-300 hover:-translate-y-1 hover:border-[#c5a676] hover:shadow-[0_16px_36px_-6px_rgba(15,23,42,0.12)] cursor-pointer"'
new_lookbook_container = 'className="group relative min-w-0 self-start rise-in rounded-2xl border border-slate-200/90 bg-white overflow-hidden shadow-2xs transition-all duration-200 hover:border-slate-300 hover:shadow-md flex flex-col w-full cursor-pointer"'

if old_lookbook_aspect in code:
    code = code.replace(old_lookbook_aspect, new_lookbook_aspect, 1)
    print("Updated LookbookCard aspect ratio to 5/6!")

if old_lookbook_container in code:
    code = code.replace(old_lookbook_container, new_lookbook_container, 1)
    print("Updated LookbookCard container styling!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

