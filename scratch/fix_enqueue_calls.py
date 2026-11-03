# Fix backend/app/routers/admin_ops.py
with open(r'backend\app\routers\admin_ops.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_broadcast_enqueue = '''    for cust in recipients:
        if cust.tg_id:
            formatted_text = payload.text.replace("{name}", cust.first_name or "Hurmatli mijoz")
            if payload.image_url and payload.image_url.strip():
                formatted_text = f"{payload.image_url.strip()}\\n\\n" + formatted_text
            if payload.button_text and payload.button_url:
                formatted_text += f"\\n\\n🔗 <a href='{payload.button_url}'>{payload.button_text}</a>"
            enqueue(db, cust.tg_id, formatted_text)
            sent_count += 1'''

new_broadcast_enqueue = '''    btn_txt = (payload.button_text or "").strip()
    btn_url = (payload.button_url or "").strip()
    img_url = (payload.image_url or "").strip()

    for cust in recipients:
        if cust.tg_id:
            formatted_text = payload.text.replace("{name}", cust.first_name or "Hurmatli mijoz")
            if img_url:
                if img_url.startswith("http"):
                    formatted_text = f"<a href=\\"{img_url}\\">&#8205;</a>" + formatted_text
                else:
                    formatted_text = f"{img_url}\\n\\n" + formatted_text
            
            enqueue(
                db,
                "broadcast",
                cust.tg_id,
                formatted_text,
                button_text=btn_txt,
                button_url=btn_url if btn_url.startswith("https://") else "",
            )
            sent_count += 1'''

if old_broadcast_enqueue in text:
    text = text.replace(old_broadcast_enqueue, new_broadcast_enqueue)
    with open(r'backend\app\routers\admin_ops.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed enqueue in admin_ops.py!")
else:
    print("Could not find old_broadcast_enqueue in admin_ops.py!")

# Fix backend/app/routers/admin_crm.py
with open(r'backend\app\routers\admin_crm.py', 'r', encoding='utf-8') as f:
    crm_text = f.read()

if 'enqueue(db, cust.tg_user_id, text)' in crm_text:
    crm_text = crm_text.replace('enqueue(db, cust.tg_user_id, text)', 'enqueue(db, "crm_direct", cust.tg_user_id, text)')
    with open(r'backend\app\routers\admin_crm.py', 'w', encoding='utf-8') as f:
        f.write(crm_text)
    print("Fixed enqueue in admin_crm.py!")
else:
    print("crm_text did not contain target!")
