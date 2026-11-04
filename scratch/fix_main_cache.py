with open('backend/app/main.py', 'r', encoding='utf-8') as f:
    code = f.read()

target = """    target = (DIST / full_path).resolve()
    if full_path and target.is_file() and DIST.resolve() in target.parents:
        return FileResponse(target)
    return FileResponse(DIST / "index.html")"""

replacement = """    target = (DIST / full_path).resolve()
    if full_path and target.is_file() and DIST.resolve() in target.parents:
        resp = FileResponse(target)
        if target.suffix in [".js", ".css"]:
            resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return resp
    resp = FileResponse(DIST / "index.html")
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp"""

code_norm = code.replace("\r\n", "\n")
if target in code_norm:
    code_norm = code_norm.replace(target, replacement, 1)
    with open('backend/app/main.py', 'w', encoding='utf-8') as f:
        f.write(code_norm)
    print("backend/app/main.py updated successfully!")
else:
    print("Target not found")

