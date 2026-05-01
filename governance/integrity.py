"""
Client Profile Integrity Validator

Fix in this version:
    - When client_id is set but clients/{client_id}/profile.env does not exist,
      falls back to validating root .env instead of raising FileNotFoundError.
      This allows Cloud Oven to run while the client folder is being set up.
    - Clear warning printed when falling back so the gap is visible in logs.

V2 note: Multi-client mode should have dedicated profile.env per client.
         Root .env fallback is a safe bridge, not a permanent design.
"""

import os
from pathlib import Path

REQUIRED_FIELDS = ["BUSINESS_NAME", "OPERATING_HOURS", "BUSINESS_LOCATION"]

BASE_DIR = Path(__file__).resolve().parent.parent


def validate_client_profile(client_id: str = None):
    """
    Validate client profile integrity before message execution.

    Args:
        client_id: Client folder name under clients/.
                   If None or folder missing, validates root .env.

    Raises:
        FileNotFoundError: Root .env also missing (critical failure).
        ValueError: Required fields missing from whichever profile is loaded.
    """
    from dotenv import dotenv_values

    profile_path = None

    if client_id:
        candidate = BASE_DIR / "clients" / client_id / "profile.env"
        if candidate.exists():
            profile_path = candidate
        else:
            print(f"[INTEGRITY] Warning: clients/{client_id}/profile.env not found — falling back to root .env")

    if profile_path is None:
        profile_path = BASE_DIR / ".env"

    if not profile_path.exists():
        raise FileNotFoundError(
            f"No client profile found. Checked: clients/{client_id}/profile.env and root .env"
        )

    config = dotenv_values(str(profile_path))
    missing = [f for f in REQUIRED_FIELDS if f not in config]

    if missing:
        raise ValueError(
            f"Client profile at {profile_path} missing required fields: {missing}. "
            f"All of {REQUIRED_FIELDS} must be present."
        )

    print(f"[INTEGRITY] Profile validated: {profile_path}")