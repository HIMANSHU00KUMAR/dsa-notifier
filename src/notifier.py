import logging
import urllib.parse
from typing import Optional, Dict, Any
import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class NtfyNotifier:
    """Sends rich push notifications via free ntfy.sh (Zero API key needed)."""

    def __init__(self, topic: str, timeout: int = 15):
        self.topic = topic
        self.timeout = timeout

    def send(self, message: str, title: str = "🎯 Daily DSA Problem", url: Optional[str] = None) -> bool:
        if not self.topic:
            raise ValueError("NTFY_TOPIC is not configured.")

        payload = {
            "topic": self.topic,
            "title": title,
            "message": message,
            "priority": 4,
            "tags": ["dart", "brain", "rocket"]
        }
        if url:
            payload["click"] = url
            payload["actions"] = [
                {
                    "action": "view",
                    "label": "Solve on Codeforces",
                    "url": url,
                    "clear": True
                }
            ]

        logger.info(f"Dispatching push notification to ntfy.sh/{self.topic}...")
        try:
            response = requests.post(
                "https://ntfy.sh",
                json=payload,
                timeout=self.timeout
            )
            if response.status_code == 200:
                logger.info(f"Push notification successfully delivered to ntfy.sh/{self.topic}!")
                return True
            else:
                logger.error(f"ntfy.sh error ({response.status_code}): {response.text}")
                return False
        except requests.RequestException as e:
            logger.error(f"Failed to connect to ntfy.sh: {e}")
            raise


class TelegramNotifier:
    """Sends notifications via Telegram Bot API."""

    def __init__(self, bot_token: str, chat_id: str, timeout: int = 15):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.timeout = timeout

    def send(self, message: str) -> bool:
        if not self.bot_token or not self.chat_id:
            raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required.")

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }

        logger.info(f"Sending message to Telegram chat {self.chat_id}...")
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            if response.status_code == 200:
                logger.info("Telegram notification delivered successfully!")
                return True
            else:
                logger.error(f"Telegram API error ({response.status_code}): {response.text}")
                return False
        except requests.RequestException as e:
            logger.error(f"Failed to connect to Telegram API: {e}")
            raise


class WhatsAppNotifier:
    """Handles sending WhatsApp notifications via CallMeBot or Twilio."""

    def __init__(
        self,
        phone: str = "",
        api_key: str = "",
        use_twilio: bool = False,
        twilio_sid: str = "",
        twilio_token: str = "",
        twilio_from: str = "",
        twilio_to: str = "",
        timeout: int = 25
    ):
        self.phone = phone
        self.api_key = api_key
        self.use_twilio = use_twilio
        self.twilio_sid = twilio_sid
        self.twilio_token = twilio_token
        self.twilio_from = twilio_from
        self.twilio_to = twilio_to
        self.timeout = timeout

    def send_callmebot(self, message: str) -> bool:
        if not self.phone or not self.api_key:
            raise ValueError("WHATSAPP_PHONE and CALLMEBOT_API_KEY must be configured.")

        phone_cleaned = self.phone.replace("+", "").replace(" ", "").strip()
        params = {
            "phone": phone_cleaned,
            "text": message,
            "apikey": self.api_key
        }

        logger.info(f"Sending WhatsApp message via CallMeBot to +{phone_cleaned}...")
        try:
            response = requests.get("https://api.callmebot.com/whatsapp.php", params=params, timeout=self.timeout)
            text_resp = response.text.strip().lower()
            if response.status_code == 200 and not ("error" in text_resp or "invalid" in text_resp):
                logger.info("WhatsApp message successfully dispatched by CallMeBot!")
                return True
            else:
                logger.error(f"CallMeBot error: {response.text}")
                return False
        except requests.RequestException as e:
            logger.error(f"Network error communicating with CallMeBot: {e}")
            raise

    def send_twilio(self, message: str) -> bool:
        if not self.twilio_sid or not self.twilio_token or not self.twilio_to:
            raise ValueError("Twilio credentials (SID, Token, To) must be configured.")

        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Messages.json"
        to_number = self.twilio_to if self.twilio_to.startswith("whatsapp:") else f"whatsapp:{self.twilio_to}"
        from_number = self.twilio_from if self.twilio_from.startswith("whatsapp:") else f"whatsapp:{self.twilio_from}"

        payload = {"From": from_number, "To": to_number, "Body": message}
        try:
            response = requests.post(url, data=payload, auth=HTTPBasicAuth(self.twilio_sid, self.twilio_token), timeout=self.timeout)
            return response.status_code in (200, 201)
        except requests.RequestException as e:
            logger.error(f"Network error communicating with Twilio: {e}")
            raise

    def send(self, message: str) -> bool:
        if self.use_twilio:
            return self.send_twilio(message)
        return self.send_callmebot(message)


class NotificationManager:
    """Unified manager that routes notifications to the configured channel."""

    def __init__(self, config):
        self.config = config
        self.channel = config.notification_channel

        self.ntfy = NtfyNotifier(topic=config.ntfy_topic)
        self.telegram = TelegramNotifier(bot_token=config.telegram_bot_token, chat_id=config.telegram_chat_id)
        self.whatsapp = WhatsAppNotifier(
            phone=config.whatsapp_phone,
            api_key=config.callmebot_api_key,
            use_twilio=config.use_twilio,
            twilio_sid=config.twilio_account_sid,
            twilio_token=config.twilio_auth_token,
            twilio_from=config.twilio_from_number,
            twilio_to=config.twilio_to_number
        )

    def dispatch(self, message: str, title: str = "🎯 Daily DSA Problem", url: Optional[str] = None) -> bool:
        if self.channel == "ntfy":
            return self.ntfy.send(message, title=title, url=url)
        elif self.channel == "telegram":
            return self.telegram.send(message)
        elif self.channel == "whatsapp":
            return self.whatsapp.send(message)
        else:
            # Fallback to ntfy if unknown
            logger.warning(f"Unknown channel '{self.channel}', falling back to ntfy.sh.")
            return self.ntfy.send(message, title=title, url=url)
