import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from bot import process_update

app = FastAPI()

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "timestamp": int(time.time())
    }

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/api/webhook")
async def telegram_webhook(request: Request):
    try:
        update_json = await request.json()
        await process_update(update_json)
        return JSONResponse({"ok": True})
    except Exception as e:
        print("Webhook error:", e)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
