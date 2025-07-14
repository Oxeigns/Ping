# Telegram Moderation Bot

Modern moderation bot built with **Pyrogram** and **MongoDB**.

## Features
- Automatic deletion of text and media after a configurable delay
- Dynamic abuse word filtering backed by MongoDB
- Simple admin commands for timers and abuse list management
- Owner broadcast to all groups
- Clean inline control panel
- Async functions with a global Mongo connection
- Modern Python best practices with full type hints
- Ready for Railway, Render, Heroku, or VPS deployment

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
4. Run with `python run.py`.

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

### MongoDB Setup
This project uses SQLite by default for simplicity. If you prefer MongoDB,
install `motor` and set `DATABASE_URL` to your Mongo connection string.
Update the `database` module to use `motor.motor_asyncio.AsyncIOMotorClient`
in place of `aiosqlite`.
### Example `.env`
```bash
BOT_TOKEN=your_bot_token
API_ID=12345
API_HASH=your_api_hash
OWNER_ID=1888832817
LOG_CHANNEL_ID=-1001234567890
MONGO_URI=mongodb://localhost:27017/modbot
PANEL_IMAGE=https://example.com/panel.png
DEV_URL=https://t.me/Oxeign
DEV_NAME=Oxeign
```
### Environment Variables
Edit `.env` with the following keys:

- `BOT_TOKEN` – Telegram bot token
- `API_ID` / `API_HASH` – Telegram API credentials
- `OWNER_ID` – your Telegram user ID
- `LOG_CHANNEL_ID` – channel/group ID for logs
- `MONGO_URI` – MongoDB connection string
- `PANEL_IMAGE` – optional URL or file path to an image shown with the control panel.
- `DEV_URL` – link shown in the Developer button
- `DEV_NAME` – name used in the Developer alert
- `DEBUG_UPDATES` – set to `1` to enable verbose logging of every incoming update. Useful when troubleshooting why the bot is not receiving commands.
- `banned_words.txt` – list of words or phrases to filter, one per line.

## Troubleshooting MTProto connectivity on Render

Some hosts may block or throttle Telegram's MTProto ports. To verify long polling works on your Render worker, run the following minimal script:

```bash
python mtproto_test.py
```

If the bot sends a startup message and responds to commands, MTProto is allowed. Otherwise, consider switching to HTTP-based polling using `python-telegram-bot` or `aiogram`.

A basic HTTP polling example using `python-telegram-bot` is available in `http_polling_example.py`.

## Screenshots
![Control Panel](https://example.com/screenshot.png)

## Support
- 📢 [Support Channel](https://t.me/botsyard)
- 💬 [Support Group](https://t.me/+Sn1PMhrr_nIwM2Y1)

## Credits
Developed by [Oxeign](https://t.me/Oxeign). Pull requests are welcome!
