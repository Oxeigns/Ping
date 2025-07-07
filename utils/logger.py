async def log_action(app, text: str) -> None:
    chat_id = getattr(app.config, "LOG_CHANNEL", None)
    if chat_id:
        try:
            await app.send_message(chat_id, text)
        except Exception:
            pass
