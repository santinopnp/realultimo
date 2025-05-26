@app.post("/webhook")
async def bold_webhook(request: Request):
    data = await request.json()
    print("Webhook data:", data)
    try:
        telegram_user_id = int(data["metadata"]["telegram_user_id"])
        username = data["metadata"].get("username", "")
        plan = data["product"]["name"]
    except Exception as e:
        print("Error leyendo campos:", e)
        return {"error": "Campos faltantes"}, status.HTTP_400_BAD_REQUEST

    days = 7
    if "Month" in plan:
        days = 30
    elif "Frequent" in plan or "3 meses" in plan or "3 Month" in plan:
        days = 90
    elif "Year" in plan or "Año" in plan or "Année" in plan:
        days = 365
    expires_at = datetime.now() + timedelta(days=days)
    user_memberships[telegram_user_id] = {
        "username": username,
        "expires_at": expires_at,
        "plan": plan
    }
    for chat_id in CHANNELS_AND_GROUPS:
        await add_user_to_chat(telegram_user_id, chat_id)
    print(f"Usuario {telegram_user_id} agregado a grupos hasta {expires_at}")
    return {"status": "usuario registrado y añadido a canales"}, 200
