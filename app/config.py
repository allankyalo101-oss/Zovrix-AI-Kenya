"""
app/config.py — Zovrix AI Kenya unified settings loader.

Multi-client version: each client has its own Twilio credentials.
Missing required fields raise a clear error at startup.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Application Mode ──────────────────────────────────
    MOCK_MODE: bool = False

    # ── Groq AI ───────────────────────────────────────────
    GROQ_API_KEY: str

    # ── Twilio — fallback (used if client-specific not set) ──
    TWILIO_ACCOUNT_SID:    str = ""
    TWILIO_AUTH_TOKEN:     str = ""
    TWILIO_WHATSAPP_NUMBER:str = ""

    # ── Twilio — CloudOven account ────────────────────────
    CLOUDOVEN_TWILIO_SID:    str = ""
    CLOUDOVEN_TWILIO_TOKEN:  str = ""
    CLOUDOVEN_TWILIO_NUMBER: str = ""  # e.g. whatsapp:+14155238886

    # ── Twilio — Kisha-Tech account ───────────────────────
    KISHATECH_TWILIO_SID:    str = ""
    KISHATECH_TWILIO_TOKEN:  str = ""
    KISHATECH_TWILIO_NUMBER: str = ""  # Kisha-Tech sandbox number

    # ── Owner numbers per client ──────────────────────────
    CLOUDOVEN_OWNER_WHATSAPP: str = ""   # +254712191702
    KISHATECH_OWNER_WHATSAPP: str = ""   # +254742891721
    OWNER_WHATSAPP_NUMBER:    str = ""   # legacy fallback

    # ── Business Profile (CloudOven default) ──────────────
    BUSINESS_NAME:     str = "CloudOven"
    BUSINESS_TYPE:     str = "Online Cookie Shop"
    SERVICES_OFFERED:  str = "Cookies"
    BUSINESS_LOCATION: str = "Kenya Israel, Machakos"
    OPERATING_HOURS:   str = "9:00am to 7:00pm Monday to Saturday"
    TONE_PREFERENCE:   str = "Warm Kenyan English with light Swahili"
    ESCALATION_CONTACT:str = ""
    ESCALATION_MESSAGE:str = "Asante for reaching out to CloudOven 😊 Let me check that with our team and get back to you shortly."
    CLOUDOVEN_WEBSITE:  str = "https://cloudoven.vercel.app"

    # ── Operator / Alerting ───────────────────────────────
    OPERATOR_EMAIL: str = ""
    SMTP_SERVER:    str = "smtp.gmail.com"
    SMTP_PORT:      int = 587
    SMTP_USER:      str = ""
    SMTP_PASSWORD:  str = ""

    # ── Payment (IntaSend) ────────────────────────────────
    INTASEND_PUBLIC_KEY: str = ""
    INTASEND_SECRET_KEY: str = ""
    INTASEND_ENV:        str = "sandbox"
    INTASEND_API_KEY:    str = ""   # legacy — kept for compat

    # ── Database (Supabase — CloudOven) ───────────────────
    DATABASE_URL:        str = ""
    SUPABASE_URL:        str = ""
    SUPABASE_KEY:        str = ""          # anon key
    SUPABASE_ANON_KEY:   str = ""          # alias
    SUPABASE_SERVICE_KEY:str = ""          # service role — server-side only

    # ── Database (Supabase — Kisha-Tech) ──────────────────
    KISHATECH_SUPABASE_URL: str = ""
    KISHATECH_SUPABASE_KEY: str = ""       # service role for backend reads

    # ── Multi-client routing ──────────────────────────────
    DEFAULT_CLIENT_ID: str = "cloud_oven"

    def supabase_service_key(self) -> str:
        """Return whichever service key is populated."""
        return self.SUPABASE_SERVICE_KEY or self.SUPABASE_KEY or self.SUPABASE_ANON_KEY


settings = Settings()  # type: ignore