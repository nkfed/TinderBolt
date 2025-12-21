print(">>> api/webhook.py LOADED")

import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "timestamp": int(time.time())
    }

@app.post("/api/webhook")
async def telegram_webhook(request: Request):
    try:
        raw = await request.body()
        try:
            text = raw.decode("utf-8")
        except:
            text = raw.decode("latin-1", errors="replace")

        import json
        update_json = json.loads(text)

        # Динамічний імпорт — тільки при запиті
        from bot import process_update

        await process_update(update_json)
        return JSONResponse({"ok": True})
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print("=== EXCEPTION START ===")
        print(tb)
        print("=== EXCEPTION END ===")
        return {"ok": False, "error": repr(e)}

# Vercel очікує саме цю змінну
vercel_app = app