from fastapi import FastAPI, Request, status
import httpx
import os
from datetime import datetime, timedelta

app = FastAPI()

TELEGRAM_BOT_TOKEN = "7899263814:AAFfIAxbqwscUUZgEgXcPLCfcH9g53dtpoE"
CHANNELS_AND_GROUPS = [
    -1002201821366,   # Canal/grupo 1
    -1002258831170,   # Canal/grupo 2
    -1001834990266    # Canal/grupo 3
]
user_memberships = {}

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/webhook")
async def bold_webhook(request: Request):
    data = await request.json()
    print("Webhook data:", data)
    return {"status": "received"}

# (El resto de tus funciones pueden quedarse igual, pero no se usarán mientras debugueas solo el webhook)
async def add_user_to_chat(user_id, chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/inviteToChat"
    payload = {"chat_id": chat_id, "user_id": user_id}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)
        print("Invite:", r.status_code, r.text)

from fastapi_utils.tasks import repeat_every

@app.on_event("startup")
@repeat_every(seconds=60 * 60 * 24)
async def check_expired_memberships():
    print("Verificando membresías expiradas...")
    now = datetime.now()
    to_remove = [uid for uid, info in user_memberships.items() if info["expires_at"] < now]
    for user_id in to_remove:
        for chat_id in CHANNELS_AND_GROUPS:
            await remove_user_from_chat(user_id, chat_id)
        print(f"Usuario {user_id} removido de todos los canales por expiración.")
        del user_memberships[user_id]

async def remove_user_from_chat(user_id, chat_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/kickChatMember"
    payload = {"chat_id": chat_id, "user_id": user_id}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload)
        print("Kick:", r.status_code, r.text)
