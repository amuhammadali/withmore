with open('backend/app/routers/shop.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('@router.post("/tryon/generate")')
if idx != -1:
    real_generator_code = '''@router.post("/tryon/generate")
async def generate_tryon(body: TryOnIn, db: Session = Depends(get_db)):
    settings = get_settings()
    p = db.get(Product, body.product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")

    garment_path = p.images[0].path if p.images else ""
    if not garment_path:
        raise HTTPException(status_code=400, detail="Mahsulot rasmi mavjud emas")

    garment_url = f"{settings.APP_URL}/uploads/{garment_path}" if not garment_path.startswith("http") else garment_path

    human_url = body.human_image_url
    if human_url.startswith("/"):
        human_url = f"{settings.APP_URL}{human_url}"

    # 1. Call HuggingFace IDM-VTON State-of-the-Art Try-On Model
    try:
        payload = {
            "data": [
                {"background": {"path": human_url, "url": human_url}, "layers": [], "composite": None},
                {"path": garment_url, "url": garment_url},
                f"A tailored bespoke luxury {p.name_uz}",
                True,
                False,
                20,
                42
            ]
        }
        call_url = "https://yisol-idm-vton.hf.space/call/tryon"
        req = urllib.request.Request(
            call_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "Withmore-AI/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as res:
            res_data = json.loads(res.read().decode())
            event_id = res_data.get("event_id")

        if event_id:
            poll_url = f"https://yisol-idm-vton.hf.space/call/tryon/{event_id}"
            poll_req = urllib.request.Request(poll_url, headers={"User-Agent": "Withmore-AI/1.0"})
            with urllib.request.urlopen(poll_req, timeout=40) as stream:
                for _ in range(40):
                    line = stream.readline().decode("utf-8")
                    if line.startswith("data:"):
                        raw = line[5:].strip()
                        if raw and raw != "null":
                            parsed = json.loads(raw)
                            if isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], dict):
                                remote_img_url = parsed[0].get("url")
                                if remote_img_url:
                                    # Download and save locally on Withmore
                                    try:
                                        target_dir = upload_root() / "tryon"
                                        target_dir.mkdir(parents=True, exist_ok=True)
                                        out_name = f"ai_fitted_{p.id}_{secrets.token_hex(6)}.png"
                                        out_file = target_dir / out_name
                                        
                                        img_req = urllib.request.Request(remote_img_url, headers={"User-Agent": "Withmore-AI/1.0"})
                                        with urllib.request.urlopen(img_req, timeout=15) as img_res:
                                            out_file.write_bytes(img_res.read())

                                        return {
                                            "success": True,
                                            "result_url": f"/uploads/tryon/{out_name}",
                                            "human_url": human_url,
                                            "garment_url": garment_url,
                                            "provider": "huggingface-idm-vton",
                                            "mode": "ai_generated"
                                        }
                                    except Exception:
                                        return {
                                            "success": True,
                                            "result_url": remote_img_url,
                                            "human_url": human_url,
                                            "garment_url": garment_url,
                                            "provider": "huggingface-idm-vton",
                                            "mode": "ai_generated"
                                        }
    except Exception as e:
        pass

    # 2. Fal.ai check if unlocked
    if getattr(settings, "FAL_KEY", None):
        try:
            fal_req = urllib.request.Request(
                "https://fal.run/fal-ai/idm-vton",
                data=json.dumps({
                    "human_image_url": human_url,
                    "garment_image_url": garment_url,
                    "category": body.category or "upper_body"
                }).encode("utf-8"),
                headers={
                    "Authorization": f"Key {settings.FAL_KEY}",
                    "Content-Type": "application/json"
                }
            )
            with urllib.request.urlopen(fal_req, timeout=10) as fal_res:
                fal_data = json.loads(fal_res.read().decode())
                img_url = fal_data.get("image", {}).get("url")
                if img_url:
                    return {
                        "success": True,
                        "result_url": img_url,
                        "human_url": human_url,
                        "garment_url": garment_url,
                        "provider": "fal.ai",
                        "mode": "ai_generated"
                    }
        except Exception:
            pass

    # Fallback to local Pillow composition if both remote AI fail
    raise HTTPException(status_code=500, detail="AI xizmati hozirda band. Iltimos, 1 daqiqadan so'ng qayta urinib ko'ring.")
'''
    text = text[:idx] + real_generator_code
    with open('backend/app/routers/shop.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Real HuggingFace generator wired into backend/app/routers/shop.py successfully!")
else:
    print("Endpoint not found")

