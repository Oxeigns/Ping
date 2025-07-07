# Telegram Moderation Bot

A modular Telegram bot built with **Pyrogram** for automated AI‑powered moderation.

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
1. Copy `.env.example` to `.env` and fill in **API_ID**, **API_HASH**, **BOT_TOKEN**, **OWNER_ID**, **DATABASE_URL** and API keys.
2. Install requirements with `pip install -r requirements.txt`.
3. Run the bot with `python -m run`.

### VPS (systemd)
Place `pingbot.service` in `/etc/systemd/system/`, adjust paths, then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pingbot
sudo systemctl start pingbot
```

### Render.com
Create a new Web Service and point it to this repository. Render will use `render.yaml` for configuration.

### Heroku or Other Platforms
A simple `Procfile` is provided for platforms that require it:

```
worker: python -m run
```

### API Usage
The bot requires two external APIs:

1. **Perspective API** – provides the `TOXICITY_API_KEY` used for text moderation.
2. **Sightengine** – used for image moderation via `SIGHTENGINE_USER` and `SIGHTENGINE_SECRET`.

Sign up for each service, obtain the credentials and place them in the `.env` file.

## API Keys
- [Perspective API](https://www.perspectiveapi.com/) for toxicity detection
- [Sightengine](https://sightengine.com/) for image moderation

