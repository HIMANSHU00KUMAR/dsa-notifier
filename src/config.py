import os
import re
from dataclasses import dataclass, field
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    # Codeforces configuration
    cf_handle: str = field(default_factory=lambda: os.getenv("CF_HANDLE", "HIMANSHU_KUMAR0").strip())
    min_rating: Optional[int] = field(
        default_factory=lambda: int(os.getenv("MIN_RATING")) if os.getenv("MIN_RATING") and os.getenv("MIN_RATING").strip().isdigit() else 800
    )
    max_rating: Optional[int] = field(
        default_factory=lambda: int(os.getenv("MAX_RATING")) if os.getenv("MAX_RATING") and os.getenv("MAX_RATING").strip().isdigit() else 1200
    )
    preferred_tags: List[str] = field(
        default_factory=lambda: [t.strip() for t in os.getenv("PREFERRED_TAGS", "").split(",") if t.strip()]
    )

    # Notification Channel: 'ntfy', 'telegram', 'whatsapp' (callmebot/twilio)
    notification_channel: str = field(
        default_factory=lambda: os.getenv("NOTIFICATION_CHANNEL", "ntfy").strip().lower()
    )

    # 1. ntfy.sh (Zero API key needed, free phone push notifications)
    ntfy_topic: str = field(
        default_factory=lambda: os.getenv("NTFY_TOPIC", "himanshu-dsa-daily").strip()
    )

    # 2. Telegram configuration
    telegram_bot_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", "").strip())
    telegram_chat_id: str = field(default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", "").strip())

    # 3. WhatsApp configuration (CallMeBot / Twilio)
    whatsapp_phone: str = field(default_factory=lambda: os.getenv("WHATSAPP_PHONE", "918789305369").strip())
    callmebot_api_key: str = field(default_factory=lambda: os.getenv("CALLMEBOT_API_KEY", "").strip())
    use_twilio: bool = field(default_factory=lambda: os.getenv("USE_TWILIO", "false").lower() in ("true", "1", "yes"))
    twilio_account_sid: str = field(default_factory=lambda: os.getenv("TWILIO_ACCOUNT_SID", "").strip())
    twilio_auth_token: str = field(default_factory=lambda: os.getenv("TWILIO_AUTH_TOKEN", "").strip())
    twilio_from_number: str = field(default_factory=lambda: os.getenv("TWILIO_FROM_NUMBER", "whatsapp:+14155238886").strip())
    twilio_to_number: str = field(default_factory=lambda: os.getenv("TWILIO_TO_NUMBER", "").strip())

    # History file path
    history_file: str = field(
        default_factory=lambda: os.getenv(
            "HISTORY_FILE",
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "history", "sent_problems.json")
        )
    )

    def validate(self) -> List[str]:
        """Validate configuration settings based on chosen channel."""
        errors = []

        if self.notification_channel == "ntfy":
            if not self.ntfy_topic:
                errors.append("NTFY_TOPIC is required for ntfy push notifications.")

        elif self.notification_channel == "telegram":
            if not self.telegram_bot_token:
                errors.append("TELEGRAM_BOT_TOKEN is required for Telegram notifications.")
            if not self.telegram_chat_id:
                errors.append("TELEGRAM_CHAT_ID is required for Telegram notifications.")

        elif self.notification_channel == "whatsapp":
            if self.use_twilio:
                if not self.twilio_account_sid or not self.twilio_auth_token or not self.twilio_to_number:
                    errors.append("Twilio credentials (SID, Token, To) required when USE_TWILIO=true")
            else:
                if not self.whatsapp_phone or not self.callmebot_api_key:
                    errors.append("WHATSAPP_PHONE and CALLMEBOT_API_KEY are required for CallMeBot WhatsApp delivery.")

        return errors


def get_config() -> Config:
    return Config()
