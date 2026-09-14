from dataclasses import dataclass

import httpx
import truststore

from app.core.config import get_settings


@dataclass(frozen=True)
class TelegramResult:
    status: str
    error_code: str | None = None


def format_alert_message(*, field_name: str, risk_type: str, recommendation: str) -> str:
    return (
        f"AgroGuard alert\nField: {field_name}\n"
        f"Risk: {risk_type}\nRecommended action: {recommendation}"
    )


def send_telegram_message(message: str) -> TelegramResult:
    settings = get_settings()
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return TelegramResult(status="suppressed", error_code="telegram_not_configured")

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token.get_secret_value()}/sendMessage"
    try:
        # Use the OS certificate store so corporate/network TLS certificates trusted
        # by Windows are honored without weakening HTTPS verification.
        with httpx.Client(verify=truststore.SSLContext(), timeout=5.0) as client:
            response = client.post(
                url,
                json={"chat_id": settings.telegram_chat_id, "text": message},
            )
        response.raise_for_status()
        return TelegramResult(status="sent")
    except (httpx.HTTPError, ValueError):
        return TelegramResult(status="failed", error_code="telegram_delivery_failed")
