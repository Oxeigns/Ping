import aiohttp
import logging
from config import Config

logger = logging.getLogger(__name__)


async def check_toxicity(text: str) -> float:
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
                    logger.error("Perspective API returned status %s", resp.status)
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
    except Exception as exc:
        logger.exception("Unexpected error in toxicity check: %s", exc)

    return 0.0


async def check_image(file: bytes) -> dict:
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
                    logger.error("Sightengine API returned status %s", resp.status)
                    return {}
                result = await resp.json()
                logger.debug("✅ Sightengine response: %s", result)
                return result
    except aiohttp.ClientError as exc:
        logger.error("🌐 Sightengine API connection error: %s", exc)
    except Exception as exc:
        logger.exception("Unexpected error in image check: %s", exc)

    return {}
