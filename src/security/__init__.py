"""
Security utilities for the Enterprise AI Gateway
"""

import os
import re
import logging
import requests
from fastapi import HTTPException, Depends, status
from fastapi.security import APIKeyHeader

logger = logging.getLogger(__name__)

# --- Security Configuration ---
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
SERVICE_API_KEY = os.getenv("SERVICE_API_KEY")
ENABLE_PROMPT_INJECTION_CHECK = os.getenv("ENABLE_PROMPT_INJECTION_CHECK", "true").lower() == "true"

# --- Prompt Injection Detection ---
INJECTION_PATTERNS = [
    # Existing patterns - direct override attempts
    r"ignore\s+(all\s+)?(previous|above|prior)\s+instructions?",
    r"disregard\s+(all\s+)?(previous|above|prior)\s+instructions?",
    r"you\s+are\s+now",
    r"system\s*:\s*",

    # Demonstration/example requests for attacks
    r"(demonstrate|show|give\s+me|provide).{0,30}(injection|jailbreak|exploit|attack|bypass|hack)",
    r"(example|sample|demo).{0,20}(of|for).{0,20}(injection|jailbreak|exploit|attack|bypass)",
    r"(how\s+to|how\s+would|how\s+do\s+i|how\s+do\s+you).{0,30}(inject|jailbreak|exploit|bypass|hack)",
    r"by\s+demonstrating.{0,20}(injection|jailbreak|exploit|attack|bypass|one)",
    r"(injection|jailbreak|exploit|attack).{0,20}by\s+demonstrating",

    # Simulate/role-play attack requests
    r"(simulate|emulate|replicate|recreate).{0,30}(attack|injection|exploit|breach|hack)",
    r"(pretend|act\s+as\s+if|imagine).{0,30}(hacked|breached|compromised|no.{0,10}filter)",
]

def detect_prompt_injection(prompt: str) -> bool:
    """Detect potential prompt injection attacks"""
    if not ENABLE_PROMPT_INJECTION_CHECK:
        return False
    prompt_lower = prompt.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, prompt_lower, re.IGNORECASE):
            return True
    return False

# --- PII Detection ---
PII_PATTERNS = {
    # Existing patterns
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "tax_id": r"\b\d{2}-\d{7}\b",

    # API Keys - OpenAI/Anthropic style (sk-proj-xxx, sk-ant-xxx)
    "api_key_openai": r"\bsk-[a-zA-Z0-9\-_]{20,}\b",
    # API Keys - AWS access keys
    "api_key_aws": r"\bAKIA[0-9A-Z]{16}\b",
    # API Keys - Generic patterns with labels
    "api_key_labeled": r"(api[_\-]?key|apikey|api[_\-]?secret|secret[_\-]?key|access[_\-]?token|bearer)[\s:=]+\S+",

    # Passport Numbers - 1-2 letters followed by 6-9 digits
    "passport": r"\b[A-Z]{1,2}[\s\-]?\d{6,9}\b",

    # Driver's License - Letter followed by digit groups
    "drivers_license_dashed": r"\b[A-Z]\d{3}[\-\s]?\d{4}[\-\s]?\d{4}\b",
    "drivers_license_simple": r"\b[A-Z]\d{6,12}\b",

    # Medical Records - DOB patterns
    "medical_dob": r"(DOB|date\s+of\s+birth|d\.o\.b\.?)[\s:]+\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}",
    # Medical Records - MRN patterns
    "medical_mrn": r"(MRN|medical\s+record|patient\s+id|patient\s+number)[\s:#\-]+\d{4,}",

    # Phone Numbers - US formats
    "phone_us": r"\b(\+?1[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}\b",
    # Phone Numbers - International with + prefix
    "phone_intl": r"\+\d{1,3}[\s\-.]?\d{2,4}[\s\-.]?\d{3,4}[\s\-.]?\d{3,4}\b",

    # IBAN - International Bank Account Number
    "iban": r"\b[A-Z]{2}\d{2}[\s]?[A-Z0-9]{4}[\s]?[A-Z0-9]{4}[\s]?[A-Z0-9]{4}[\s]?[A-Z0-9]{0,14}\b",

    # Password - Labeled patterns
    "password_labeled": r"(password|passwd|pwd|pass)[\s:=]+\S+",
    # Database connection strings with credentials
    "db_connection": r"(postgres|mysql|mongodb|redis)://[^:]+:[^@]+@",
}

def detect_pii(prompt: str) -> dict:
    """Detect PII in prompt, returns {has_pii: bool, pii_types: list, matches: dict}"""
    matches = {}
    pii_types = []

    for pii_type, pattern in PII_PATTERNS.items():
        found = re.findall(pattern, prompt, re.IGNORECASE)
        if found:
            pii_types.append(pii_type)
            matches[pii_type] = len(found)

    return {
        "has_pii": len(pii_types) > 0,
        "pii_types": pii_types,
        "matches": matches
    }

# --- API Key Validation ---
async def validate_api_key(api_key: str = Depends(api_key_header)):
    """Validate API key for request authentication"""
    if not SERVICE_API_KEY:
        raise HTTPException(status_code=500, detail="Server misconfiguration: API Key missing")
    if api_key != SERVICE_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key


# --- Gemini Safety Filter for Toxicity Detection ---
# Uses Gemini's built-in content safety that returns HARM_CATEGORY_* ratings
# Uses GEMINI_MODEL env var or defaults to gemini-2.5-flash
def get_gemini_safety_url():
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    return f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

# --- Lakera Guard API (Fallback) ---
LAKERA_API_URL = "https://api.lakera.ai/v2/guard"

# Gemini harm categories (all available categories)
HARM_CATEGORIES = [
    "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "HARM_CATEGORY_HATE_SPEECH",
    "HARM_CATEGORY_HARASSMENT",
    "HARM_CATEGORY_DANGEROUS_CONTENT",
    "HARM_CATEGORY_CIVIC_INTEGRITY",
]

def detect_toxicity(text: str) -> dict:
    """
    Detect toxic content using Gemini's built-in safety filters.
    Uses GEMINI_API_KEY environment variable for authentication.
    Gemini 2.5 models handle safety by refusing harmful content.
    Returns: {is_toxic: bool, scores: dict, blocked_categories: list, error: str|None}
    """
    # Read API key at runtime to pick up HF Spaces secrets
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        logger.warning("GEMINI_API_KEY not configured, falling back to Lakera")
        return detect_toxicity_lakera(text)

    try:
        # Ask Gemini to classify if the content is harmful
        classification_prompt = f"""Analyze this text and determine if it requests harmful content.
Respond with ONLY one of these categories, or "SAFE" if harmless:
- SEXUALLY_EXPLICIT (nude, porn, explicit sexual content)
- HATE_SPEECH (racism, discrimination, slurs)
- HARASSMENT (threats, bullying, intimidation)
- DANGEROUS_CONTENT (weapons, drugs, violence, self-harm)
- CIVIC_INTEGRITY (election fraud, voter suppression)

Text to analyze: "{text}"

Category:"""

        payload = {
            "contents": [{"parts": [{"text": classification_prompt}]}],
        }

        response = requests.post(
            f"{get_gemini_safety_url()}?key={api_key}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code != 200:
            error_detail = ""
            try:
                error_detail = response.json().get("error", {}).get("message", "")
            except:
                pass
            logger.warning(f"Gemini API error {response.status_code}: {error_detail}, falling back to Lakera")
            return detect_toxicity_lakera(text)

        data = response.json()
        blocked_categories = []
        scores = {}

        # Check if request was blocked at prompt level
        if "promptFeedback" in data:
            feedback = data["promptFeedback"]
            if feedback.get("blockReason"):
                blocked_categories.append(feedback["blockReason"])
                return {
                    "is_toxic": True,
                    "scores": {"BLOCKED": 1.0},
                    "blocked_categories": blocked_categories,
                    "error": None
                }

        # Parse Gemini's classification response
        if "candidates" in data and data["candidates"]:
            response_text = ""
            for part in data["candidates"][0].get("content", {}).get("parts", []):
                response_text += part.get("text", "")

            response_text = response_text.strip().upper()

            # Check for harmful categories
            harmful_categories = [
                "SEXUALLY_EXPLICIT", "HATE_SPEECH", "HARASSMENT",
                "DANGEROUS_CONTENT", "CIVIC_INTEGRITY"
            ]

            for category in harmful_categories:
                if category in response_text:
                    blocked_categories.append(f"HARM_CATEGORY_{category}")
                    scores[f"HARM_CATEGORY_{category}"] = 0.9

            # If Gemini says SAFE or doesn't match categories
            if not blocked_categories:
                scores["SAFE"] = 1.0

        return {
            "is_toxic": len(blocked_categories) > 0,
            "scores": scores,
            "blocked_categories": blocked_categories,
            "error": None
        }

    except requests.exceptions.Timeout:
        logger.warning("Gemini API timeout, falling back to Lakera")
        return detect_toxicity_lakera(text)
    except Exception as e:
        logger.warning(f"Gemini API exception: {e}, falling back to Lakera")
        return detect_toxicity_lakera(text)


def detect_toxicity_lakera(text: str) -> dict:
    """
    Fallback toxicity detection using Lakera Guard API.
    Uses LAKERA_API_KEY environment variable for authentication.
    Returns: {is_toxic: bool, scores: dict, blocked_categories: list, error: str|None}
    """
    api_key = os.getenv("LAKERA_API_KEY")

    if not api_key:
        logger.warning("LAKERA_API_KEY not configured, skipping toxicity check")
        # Both Gemini and Lakera unavailable - allow request to proceed
        return {
            "is_toxic": False,
            "scores": {},
            "blocked_categories": [],
            "error": None  # Don't error, just skip check
        }

    try:
        payload = {
            "messages": [{"content": text, "role": "user"}]
        }

        response = requests.post(
            LAKERA_API_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=10
        )

        if response.status_code != 200:
            error_detail = ""
            try:
                error_detail = response.json().get("error", response.text)
            except:
                error_detail = response.text
            logger.warning(f"Lakera API error {response.status_code}: {error_detail}")
            # Both APIs failed - allow request to proceed
            return {
                "is_toxic": False,
                "scores": {},
                "blocked_categories": [],
                "error": None  # Don't block user, just skip check
            }

        data = response.json()
        blocked_categories = []
        scores = {}

        # Lakera returns categories with flagged status
        # Check for flagged content in results
        results = data.get("results", [])
        for result in results:
            categories = result.get("categories", {})
            for category, flagged in categories.items():
                if flagged:
                    blocked_categories.append(f"LAKERA_{category.upper()}")
                    scores[f"LAKERA_{category.upper()}"] = 1.0
                else:
                    scores[f"LAKERA_{category.upper()}"] = 0.0

            # Also check category_scores for more detail
            category_scores = result.get("category_scores", {})
            for category, score in category_scores.items():
                scores[f"LAKERA_{category.upper()}"] = score

        # Check top-level flagged status
        is_flagged = data.get("flagged", False)
        if is_flagged and not blocked_categories:
            blocked_categories.append("LAKERA_FLAGGED")

        return {
            "is_toxic": is_flagged or len(blocked_categories) > 0,
            "scores": scores,
            "blocked_categories": blocked_categories,
            "error": None
        }

    except requests.exceptions.Timeout:
        logger.warning("Lakera API timeout")
        return {
            "is_toxic": False,
            "scores": {},
            "blocked_categories": [],
            "error": None  # Don't block user
        }
    except Exception as e:
        logger.warning(f"Lakera API exception: {e}")
        return {
            "is_toxic": False,
            "scores": {},
            "blocked_categories": [],
            "error": None  # Don't block user
        }