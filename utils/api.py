import aiohttp
import logging

from config import Config

logger = logging.getLogger(__name__)


async def check_toxicity(text: str) -> float:
    """Return Perspective API toxicity score between 0 and 1."""
    url = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"
    params = {"key": Config.PERSPECTIVE_API_KEY}
    payload = {
        "comment": {"text": text},
        "languages": ["en"],
        "requestedAttributes": {"TOXICITY": {}},
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, params=params, timeout=10) as resp:
                data = await resp.json()
                score = (
                    data.get("attributeScores", {})
                    .get("TOXICITY", {})
                    .get("summaryScore", {})
                    .get("value", 0.0)
                )
                return float(score)
    except Exception as exc:
        logger.error("Perspective API error: %s", exc)
        return 0.0


async def check_image(file: bytes) -> dict:
    """Return NSFW probabilities from Sightengine."""
    url = "https://api.sightengine.com/1.0/check.json"
    params = {
        "models": "nudity,wad",
        "api_user": Config.SIGHTENGINE_USER,
        "api_secret": Config.SIGHTENGINE_SECRET,
    }
    data = aiohttp.FormData()
    data.add_field("media", file, filename="image.jpg", content_type="image/jpeg")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, params=params, timeout=10) as resp:
                return await resp.json()
    except Exception as exc:
        logger.error("Sightengine API error: %s", exc)
        return {}
