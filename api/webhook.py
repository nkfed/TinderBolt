print(">>> api/webhook.py LOADED")

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

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
        print("Webhook error:", e)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

# Vercel очікує саме цю змінну
vercel_app = app