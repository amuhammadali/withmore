with open('backend/app/routers/shop.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    'raise HTTPException(status_code=500, detail="AI xizmati hozirda band. Iltimos, 1 daqiqadan so\'ng qayta urinib ko\'ring.")',
    'raise HTTPException(status_code=500, detail=f"AI xizmati: {last_err}")'
)

text = text.replace(
    'except Exception as e:\n        pass\n\n    # 2. Fal.ai check',
    'except Exception as e:\n        last_err = f"HF error: {str(e)}"\n\n    # 2. Fal.ai check'
)

text = text.replace(
    '# 1. Call HuggingFace',
    'last_err = "Unknown error"\n    # 1. Call HuggingFace'
)

with open('backend/app/routers/shop.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated shop.py to expose exact error!")

