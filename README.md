# Telegram Moderation Bot

A modular Telegram bot built with **Pyrogram** for basic group moderation.

## Features
- Manual text filtering using a configurable `banned_words.txt` file
- Warn and mute users when banned words are used
- Admin approval system and warning management
- Broadcast system for the owner
- Works in private chats and groups
- Deployment ready for VPS (systemd) and Render.com

## Commands
- `/start` `/menu` `/help` – show control panel
- `/ping` – check bot status
- `/approve` `/unapprove` `/approved` `/rmwarn` – admin tools
- `/broadcast <text>` – owner broadcast

## Usage
1. Start the bot in a private chat or add it to a group.
2. Use `/menu` to open the control panel. If `PANEL_IMAGE` is configured, the panel is shown with the image you provide.
3. Explore the inline buttons to configure groups or broadcast messages.

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
Create a new **Background Worker** pointing to this repository. Render uses `render.yaml` for configuration. Render defaults to the latest Python version which may be incompatible with pinned dependencies. This project targets **Python 3.11**, so the repository includes a `runtime.txt` and `.python-version` file to explicitly set the Python version during deployment.
`render.yaml` installs packages using the `--only-binary=:all:` flag to ensure pre-built wheels.
### Environment Variables
Edit `.env` with the following keys:

- `BOT_TOKEN` – Telegram bot token
- `API_ID` / `API_HASH` – Telegram API credentials
- `OWNER_ID` – your Telegram user ID
- `LOG_CHANNEL_ID` – channel/group ID for logs
- `DB_FILE` – path to the SQLite DB file. By default the value of `DATABASE_URL` is used unless it looks like a Postgres connection string. This avoids issues with hosts like Render that automatically define `DATABASE_URL` for Postgres.
- `PANEL_IMAGE` – optional URL or file path to an image shown with the control panel.
- `DEBUG_UPDATES` – set to `1` to enable verbose logging of every incoming update. Useful when troubleshooting why the bot is not receiving commands.
- `banned_words.txt` – list of words or phrases to filter, one per line.

## Troubleshooting MTProto connectivity on Render

Some hosts may block or throttle Telegram's MTProto ports. To verify long polling works on your Render worker, run the following minimal script:

```bash
python mtproto_test.py
```

If the bot sends a startup message and responds to commands, MTProto is allowed. Otherwise, consider switching to HTTP-based polling using `python-telegram-bot` or `aiogram`.

A basic HTTP polling example using `python-telegram-bot` is available in `http_polling_example.py`.
