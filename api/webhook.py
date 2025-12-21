print(">>> api/webhook.py LOADED")

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from bot import process_update

app = FastAPI()

@app.post("/api/webhook")
async def telegram_webhook(request: Request):
    try:
        update_json = await request.json()
        await process_update(update_json)
        return JSONResponse({"ok": True})
    except Exception as e:
        print("Webhook error:", e)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

# Vercel очікує саме цю змінну
vercel_app = app