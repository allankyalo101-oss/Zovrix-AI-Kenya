import json
import logging
from datetime import datetime, timezone
from pathlib import Path

# =================================================
# FILE PATH SETUP
# =================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_DIR  = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "interactions.json"

LOG_DIR.mkdir(parents=True, exist_ok=True)

# =================================================
# LOGGER CONFIGURATION
# =================================================
logger = logging.getLogger("sarah")
logger.setLevel(logging.INFO)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    )
    logger.addHandler(console_handler)


# =================================================
# DAILY MESSAGE COUNTER
# =================================================
TWILIO_DAILY_LIMIT = 50
TWILIO_SOFT_CUTOFF = 40   # stop complex flows at 40, keep 10 as buffer


def get_daily_message_count() -> int:
    """
    Count how many interactions have been logged today (UTC).
    Each logged interaction = 1 outgoing Twilio message consumed.
    Returns 0 if log file does not exist or cannot be read.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    count = 0

    try:
        if not LOG_FILE.exists():
            return 0

        with LOG_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    ts = record.get("timestamp", "")
                    if ts.startswith(today):
                        count += 1
                except json.JSONDecodeError:
                    continue

    except Exception as e:
        logger.warning(f"[COUNTER] Could not read daily count: {repr(e)}")

    return count


def is_approaching_daily_limit() -> bool:
    """Returns True when we have hit or passed the soft cutoff."""
    return get_daily_message_count() >= TWILIO_SOFT_CUTOFF


def is_at_daily_limit() -> bool:
    """Returns True when we are at or past the hard daily limit."""
    return get_daily_message_count() >= TWILIO_DAILY_LIMIT


# =================================================
# STRUCTURED INTERACTION LOGGER
# =================================================
def log_interaction(
    sender_last4: str = None,
    client_id: str = None,
    message_length: int = None,
    response_length: int = None,
    escalated: bool = False,
    mock_mode: bool = True,
    topic: str = None,
    confidence: str = None,
    message: str = None,
    response: str = None,
):
    """
    Append structured analytics record to interactions.json.
    Fully safe — never raises.
    """
    logger.info("[LOGGER] Writing interaction record")

    try:
        record = {
            "timestamp":       datetime.utcnow().isoformat() + "Z",
            "sender_last4":    sender_last4,
            "client_id":       client_id,
            "message_length":  message_length,
            "response_length": response_length,
            "topic":           topic,
            "confidence":      confidence,
            "escalated":       escalated,
            "mock_mode":       mock_mode,
            "message":         message,
            "response":        response,
        }

        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        logger.info("[LOGGER] Interaction logged successfully")

    except Exception as e:
        logger.warning(f"[LOGGER WARNING] Failed to write log: {repr(e)}")