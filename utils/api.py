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
