"""
Configuration for the Enterprise AI Gateway
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
SERVICE_API_KEY = os.getenv("SERVICE_API_KEY")
RATE_LIMIT = os.getenv("RATE_LIMIT", "10/minute")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
ENABLE_PROMPT_INJECTION_CHECK = os.getenv("ENABLE_PROMPT_INJECTION_CHECK", "true").lower() == "true"

# --- Toxicity Thresholds (Approach B) ---
# Lower threshold = more sensitive (blocks more content)
# Default 0.5 for hate speech (more sensitive than general 0.7)
TOXICITY_THRESHOLD_DEFAULT = float(os.getenv("TOXICITY_THRESHOLD", "0.7"))
TOXICITY_THRESHOLD_HATE = float(os.getenv("TOXICITY_THRESHOLD_HATE", "0.5"))
