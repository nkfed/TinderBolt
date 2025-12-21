from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
from bot import process_update

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/api/webhook")
async def telegram_webhook(request: Request):
    update_json = await request.json()
    # Викликати process_update з bot.py
    await process_update(update_json)
    return JSONResponse({"ok": True})

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
