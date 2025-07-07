# Telegram Moderation Bot

A modular Telegram bot built with **Pyrogram** for automated AI-powered moderation.

## Features
- Automatic text and image filtering using Google Perspective and Sightengine APIs
- Warn and mute users based on toxicity and NSFW scores
- Admin approval system and warning management
- Profile system with inline buttons and profile photo
- Broadcast system for the owner
- Works in private chats and groups
- Deployment ready for VPS (systemd) and Render.com

## Commands
- `/start` `/menu` `/help` – show control panel
- `/profile` – view user profile
- `/approve` `/unapprove` `/approved` `/rmwarn` – admin tools
- `/broadcast <text>` – owner broadcast

## Setup
1. Install **Python 3.11** and create a virtual environment (optional).
2. Copy `.env.example` to `.env` and fill the values.
3. Install requirements with `pip install -r requirements.txt`.
4. Run with `python -m run`.

### VPS (systemd)
Place `pingbot.service` in `/etc/systemd/system/`, adjust paths, then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pingbot
sudo systemctl start 