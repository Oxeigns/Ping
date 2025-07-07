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
sudo systemctl start pingbot
```

### Render.com
Create a new Web Service pointing to this repository. Render uses `render.yaml` for configuration. Render defaults to the latest Python version which may be incompatible with pinned dependencies. This project targets **Python 3.11**, so the repository includes a `runtime.txt` and `.python-version` file to explicitly set the Python version during deployment.
`render.yaml` installs packages using the `--only-binary=:all:` flag to ensure pre-built wheels.
## API Keys
- [Perspective API](https://www.perspectiveapi.com/) for toxicity detection
- [Sightengine](https://sightengine.com/) for image moderation


### Environment Variables
Edit `.env` with the following keys:

- `BOT_TOKEN` – Telegram bot token
- `API_ID` / `API_HASH` – Telegram API credentials
- `OWNER_ID` – your Telegram user ID
- `LOG_CHANNEL_ID` – channel/group ID for logs
- `PERSPECTIVE_API_KEY` – Google Perspective API key
- `IMAGE_MOD_API_KEY` – Sightengine credentials `user:secret`
- `DB_FILE` – path to the SQLite DB file. By default the value of `DATABASE_URL` is used unless it looks like a Postgres connection string. This avoids issues with hosts like Render that automatically define `DATABASE_URL` for Postgres.
