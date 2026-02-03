"""Security utilities."""

import re


def mask_sensitive(text: str) -> str:
    """
    Mask sensitive data in text for safe logging.

    Masks:
    - API keys (sk-*, sk-or-*, etc.)
    - Bearer tokens
    - Passwords in URLs
    - Generic secrets
    """
    if not text:
        return text

    # Mask API keys (various formats)
    patterns = [
        (r"(sk-or-v1-[a-zA-Z0-9]{3})[a-zA-Z0-9]{20,}", r"\1***"),
        (r"(sk-or-[a-zA-Z0-9]{2})[a-zA-Z0-9]{20,}", r"\1***"),
        (r"(sk-[a-zA-Z0-9]{2})[a-zA-Z0-9]{20,}", r"\1***"),
        (r"(Bearer\s+)[a-zA-Z0-9\-_.]+", r"\1***"),
        (r"(api[_-]?key[\"'\s:=]+)[a-zA-Z0-9\-_]{20,}", r"\1***"),
        (r"(password[\"'\s:=]+)[^\s\"']+", r"\1***"),
        (r"(token[\"'\s:=]+)[a-zA-Z0-9\-_]{20,}", r"\1***"),
    ]

    result = text
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


def is_sensitive_key(key: str) -> bool:
    """Check if a key name suggests sensitive content."""
    sensitive_words = [
        "password",
        "secret",
        "token",
        "api_key",
        "apikey",
        "auth",
        "credential",
        "private",
    ]
    key_lower = key.lower()
    return any(word in key_lower for word in sensitive_words)
