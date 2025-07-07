import httpx
from typing import Dict

from config import Config


ASYNC_CLIENT = httpx.AsyncClient()


async def check_text_toxicity(text: str) -> float:
    url = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"
    params = {"key": Config.PERSPECTIVE_API_KEY}
    payload = {
        "comment": {"text": text},
        "requestedAttributes": {"TOXICITY": {}}
    }
    try:
        r = await ASYNC_CLIENT.post(url, params=params, json=payload, timeout=5)
        r.raise_for_status()
        score = r.json()["attributeScores"]["TOXICITY"]["summaryScore"]["value"]
        return score * 100
    except Exception:
        return 0.0


async def check_image(file_path: str) -> Dict[str, bool]:
    url = "https://api.sightengine.com/1.0/check.json"
    data = {
        "models": "nudity,wad,offensive",
        "api_user": Config.SIGHTENGINE_USER,
        "api_secret": Config.SIGHTENGINE_SECRET,
    }
    try:
        with open(file_path, "rb") as f:
            r = await ASYNC_CLIENT.post(url, data=data, files={"media": f}, timeout=5)
        r.raise_for_status()
        result = r.json()
        flagged = result.get("weapon") or result.get("alcohol") or result.get("drugs") or result.get("nudity", {}).get("safe", 1) < 0.5
        return {"flagged": bool(flagged)}
    except Exception:
        return {"flagged": False}
