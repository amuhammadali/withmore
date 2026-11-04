with open('backend/app/routers/shop.py', 'r', encoding='utf-8') as f:
    text = f.read()

tryon_code = """

# ---------------- AI VIRTUAL TRY-ON (VTON) ENDPOINTS ----------------
class TryOnIn(BaseModel):
    product_id: int
    human_image_url: str
    category: str = "upper_body"


@router.post("/tryon/upload")
async def upload_tryon_photo(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Faqat rasm fayllari (JPG, PNG) qabul qilinadi")

    target_dir = upload_root() / "tryon"
    target_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename or "photo.jpg").suffix.lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        ext = ".jpg"

    file_name = f"tryon_{secrets.token_hex(8)}{ext}"
    dest = target_dir / file_name

    content = await file.read(10 * 1024 * 1024 + 1)
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Rasm hajmi 10MB dan oshmasligi kerak")

    dest.write_bytes(content)
    return {
        "url": f"/uploads/tryon/{file_name}",
        "filename": file_name
    }


@router.post("/tryon/generate")
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

    # 1. Attempt HuggingFace IDM-VTON Free Space
    try:
        call_url = "https://yisol-idm-vton.hf.space/call/tryon"
        payload = {
            "data": [
                {"background": {"path": human_url, "url": human_url}, "layers": [], "composite": None},
                {"path": garment_url, "url": garment_url},
                f"A tailored Withmore luxury {p.name_uz}",
                True,
                False,
                30,
                42
            ]
        }
        req = urllib.request.Request(
            call_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "Withmore-AI/1.0"}
        )
        with urllib.request.urlopen(req, timeout=8) as res:
            res_data = json.loads(res.read().decode())
            event_id = res_data.get("event_id")

        if event_id:
            poll_url = f"https://yisol-idm-vton.hf.space/call/tryon/{event_id}"
            poll_req = urllib.request.Request(poll_url, headers={"User-Agent": "Withmore-AI/1.0"})
            start_t = time.time()
            final_img_url = None

            while time.time() - start_t < 15:
                try:
                    with urllib.request.urlopen(poll_req, timeout=4) as poll_res:
                        lines = poll_res.read().decode().splitlines()
                        for line in lines:
                            if line.startswith("data:"):
                                raw_json = line[5:].strip()
                                parsed = json.loads(raw_json)
                                if isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], dict):
                                    final_img_url = parsed[0].get("url")
                                    break
                    if final_img_url:
                        break
                except Exception:
                    pass
                time.sleep(2)

            if final_img_url:
                return {
                    "success": True,
                    "result_url": final_img_url,
                    "human_url": human_url,
                    "garment_url": garment_url,
                    "provider": "huggingface-idm-vton",
                    "mode": "ai_generated"
                }
    except Exception:
        pass

    # 2. Attempt Fal.ai if FAL_KEY exists and unlocked
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
            with urllib.request.urlopen(fal_req, timeout=12) as fal_res:
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

    # 3. Interactive Studio fallback (Instant, zero-cost, 100% reliable)
    return {
        "success": True,
        "result_url": garment_url,
        "human_url": human_url,
        "garment_url": garment_url,
        "provider": "withmore-studio",
        "mode": "interactive_studio",
        "message": "Withmore Sartorial Fitting Studio ko'rinishi tayyorlandi!"
    }
"""

if "/tryon/generate" not in text:
    with open('backend/app/routers/shop.py', 'a', encoding='utf-8') as f:
        f.write(tryon_code)
    print("TryOn endpoints added to backend/app/routers/shop.py successfully!")
else:
    print("TryOn endpoints already exist!")
