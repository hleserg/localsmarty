import json
import time
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import requests

from config import config

logger = logging.getLogger(__name__)


class IamTokenManager:
    """Fetches and caches Yandex Cloud IAM tokens using a Service Account key (JWT exchange)."""

    def __init__(self):
        self._iam_token: Optional[str] = None
        self._expires_at: Optional[datetime] = None
        self._sa_key: Optional[dict] = None

    def _load_sa_key(self) -> dict:
        if self._sa_key:
            return self._sa_key

        if config.YC_SA_KEY_JSON:
            try:
                self._sa_key = json.loads(config.YC_SA_KEY_JSON)
            except Exception as e:
                raise ValueError(f"Invalid YC_SA_KEY_JSON: {e}")
        elif config.YC_SA_KEY_FILE:
            with open(config.YC_SA_KEY_FILE, 'r', encoding='utf-8') as f:
                self._sa_key = json.load(f)
        else:
            raise ValueError("Service account key is not provided. Set YC_SA_KEY_FILE or YC_SA_KEY_JSON.")

        required_fields = ["id", "service_account_id", "private_key"]
        for field in required_fields:
            if field not in self._sa_key:
                raise ValueError(f"Missing field '{field}' in service account key")

        return self._sa_key

    def _build_jwt(self) -> str:
        # Lazy import to avoid hard dependency at module import time
        try:
            import jwt  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "PyJWT is required to build IAM JWT. Install dependency or set YC_IAM_TOKEN/YC_API_KEY."
            ) from e
        key = self._load_sa_key()

        now = int(time.time())
        payload = {
            "aud": config.YC_IAM_ENDPOINT,
            "iss": key["service_account_id"],
            "sub": key["service_account_id"],
            "iat": now,
            # exp must be within 1 hour
            "exp": now + 3600,
        }

        headers = {
            "kid": key["id"],
            "typ": "JWT",
        }

        private_key = key["private_key"]

        # Yandex recommends PS256; fall back to RS256 if PS256 is not supported
        try:
            token = jwt.encode(payload, private_key, algorithm="PS256", headers=headers)
        except Exception:
            token = jwt.encode(payload, private_key, algorithm="RS256", headers=headers)

        # PyJWT may return bytes in older versions; ensure str
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return token

    def _request_iam_token(self) -> None:
        assertion = self._build_jwt()
        try:
            response = requests.post(
                config.YC_IAM_ENDPOINT,
                json={"jwt": assertion},
                timeout=15,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to obtain IAM token: {e}")

        data = response.json()
        iam_token = data.get("iamToken")
        expires_at_str = data.get("expiresAt")
        if not iam_token or not expires_at_str:
            raise RuntimeError("Invalid IAM token response: missing fields")

        # expiresAt example: '2025-09-06T14:00:00.123456Z'
        expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00")).astimezone(timezone.utc)

        self._iam_token = iam_token
        self._expires_at = expires_at
        logger.info("Obtained new IAM token (expires at %s)", self._expires_at.isoformat())

    def get_token(self) -> str:
        """Return a valid IAM token, refreshing it if needed."""
        # Refresh if token missing or expiring within 5 minutes
        now = datetime.now(timezone.utc)
        if not self._iam_token or not self._expires_at or (self._expires_at - now) < timedelta(minutes=5):
            self._request_iam_token()
        return self._iam_token


# Global singleton
token_manager = IamTokenManager()
