import aiohttp
import logging
from config import Config
from telegram.constants import ParseMode
import html

logger = logging.getLogger(__name__)


async def check_toxicity(text: str, bot=None) -> float:
    """
    Analyze the toxicity score of a given text using the Perspective API.
    Returns a float score between 0 (clean) and 1 (toxic).
    """
    url = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"
    params = {"key": Config.PERSPECTIVE_API_KEY}
    payload = {
        "comment": {"text": text},
        "languages": ["en"],
        "requestedAttributes": {"TOXICITY": {}},
    }

    logger.debug("🔍 Checking toxicity for text: %s", text)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, params=params, timeout=10) as resp:
                if resp.status != 200:
                    msg = f"🚨 Perspective API error {resp.status}"
                    logger.error(msg)
                    if bot and Config.LOG_CHANNEL:
                        try:
                            await bot.send_message(Config.LOG_CHANNEL, msg)
                        except Exception:
                            pass
                    return 0.0
                data = await resp.json()
                score = (
                    data.get("attributeScores", {})
                    .get("TOXICITY", {})
                    .get("summaryScore", {})
                    .get("value", 0.0)
                )
                logger.debug("✅ Toxicity score: %.3f", score)
                return float(score)
    except aiohttp.ClientError as exc:
        logger.error("🌐 Perspective API connection error: %s", exc)
        if bot and Config.LOG_CHANNEL:
            try:
                await bot.send_message(Config.LOG_CHANNEL, f"Perspective API error: {exc}")
            except Exception:
                pass
    except Exception as exc:
        logger.exception("Unexpected error in toxicity check: %s", exc)
        if bot and Config.LOG_CHANNEL:
            try:
                await bot.send_message(Config.LOG_CHANNEL, f"Perspective API exception: {html.escape(str(exc))}", parse_mode=ParseMode.HTML)
            except Exception:
                pass

    return 0.0


async def check_image(file: bytes, bot=None) -> dict:
    """
    Analyze an image using Sightengine API for NSFW, drugs, and weapons detection.
    Returns a dictionary with model probabilities.
    """
    url = "https://api.sightengine.com/1.0/check.json"
    params = {
        "models": "nudity,wad",
        "api_user": Config.SIGHTENGINE_USER,
        "api_secret": Config.SIGHTENGINE_SECRET,
    }

    data = aiohttp.FormData()
    data.add_field("media", file, filename="upload.jpg", content_type="image/jpeg")

    logger.debug("🖼️ Checking image for NSFW and moderation risks...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, params=params, timeout=10) as resp:
                if resp.status != 200:
                    msg = f"🚨 Sightengine API error {resp.status}"
                    logger.error(msg)
                    if bot and Config.LOG_CHANNEL:
                        try:
                            await bot.send_message(Config.LOG_CHANNEL, msg)
                        except Exception:
                            pass
                    return {}
                result = await resp.json()
                logger.debug("✅ Sightengine response: %s", result)
                return result
    except aiohttp.ClientError as exc:
        logger.error("🌐 Sightengine API connection error: %s", exc)
        if bot and Config.LOG_CHANNEL:
            try:
                await bot.send_message(Config.LOG_CHANNEL, f"Sightengine error: {exc}")
            except Exception:
                pass
    except Exception as exc:
        logger.exception("Unexpected error in image check: %s", exc)
        if bot and Config.LOG_CHANNEL:
            try:
                await bot.send_message(Config.LOG_CHANNEL, f"Sightengine exception: {html.escape(str(exc))}", parse_mode=ParseMode.HTML)
            except Exception:
                pass

    return {}
