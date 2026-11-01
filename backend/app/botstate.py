"""Shared mutable bot state (username, bot instance, public HTTPS tunnel URL, sender override for tests)."""
bot = None  # aiogram Bot or None
bot_username: str = ""
public_https_url: str = ""  # populated by local HTTPS tunnel when APP_URL is http://
tunnel_task = None
sender = None  # async callable(chat_id, text, photo_path, button_text, button_url); set by outbox
