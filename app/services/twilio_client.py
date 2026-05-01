from twilio.rest import Client
from app.config import settings
from app.utils.logger import logger


class TwilioService:
    def __init__(self):
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            raise ValueError("Twilio credentials not configured")

        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )

    def send_whatsapp_message(self, to_number: str, message: str):
        try:
            response = self.client.messages.create(
                from_=settings.TWILIO_WHATSAPP_NUMBER,
                body=message,
                to=to_number
            )
            logger.info(f"Message sent | SID={response.sid}")
            return response.sid
        except Exception as e:
            logger.error(f"Twilio send failed: {str(e)}")
            raise