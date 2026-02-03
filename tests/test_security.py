"""Tests for security utilities."""

import pytest
from zergbot.utils.security import mask_sensitive, is_sensitive_key


class TestMaskSensitive:
    """Test sensitive data masking."""

    def test_masks_api_key(self):
        """Should mask API keys."""
        text = "Using key sk-abc123456789012345678901234567890"
        result = mask_sensitive(text)
        assert "sk-ab***" in result
        assert "abc123456789" not in result

    def test_masks_openrouter_key(self):
        """Should mask OpenRouter keys."""
        text = "Key: sk-or-v1-abc123456789012345678901234567890"
        result = mask_sensitive(text)
        assert "sk-or-v1-abc***" in result
        assert "123456789012345678901234567890" not in result

    def test_masks_bearer_token(self):
        """Should mask Bearer tokens."""
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        result = mask_sensitive(text)
        assert "Bearer ***" in result
        assert "eyJ" not in result

    def test_masks_password_in_url(self):
        """Should mask passwords."""
        text = 'password="supersecret123"'
        result = mask_sensitive(text)
        assert "supersecret" not in result

    def test_preserves_normal_text(self):
        """Should not modify normal text."""
        text = "This is a normal message without secrets"
        result = mask_sensitive(text)
        assert result == text

    def test_handles_empty_string(self):
        """Should handle empty string."""
        assert mask_sensitive("") == ""

    def test_handles_none(self):
        """Should handle None."""
        assert mask_sensitive(None) is None


class TestIsSensitiveKey:
    """Test sensitive key detection."""

    def test_detects_password(self):
        """Should detect password keys."""
        assert is_sensitive_key("password") is True
        assert is_sensitive_key("user_password") is True
        assert is_sensitive_key("PASSWORD") is True

    def test_detects_api_key(self):
        """Should detect API key names."""
        assert is_sensitive_key("api_key") is True
        assert is_sensitive_key("apikey") is True
        assert is_sensitive_key("BRAVE_API_KEY") is True

    def test_detects_token(self):
        """Should detect token keys."""
        assert is_sensitive_key("token") is True
        assert is_sensitive_key("access_token") is True

    def test_detects_secret(self):
        """Should detect secret keys."""
        assert is_sensitive_key("secret") is True
        assert is_sensitive_key("client_secret") is True

    def test_allows_normal_keys(self):
        """Should allow normal keys."""
        assert is_sensitive_key("username") is False
        assert is_sensitive_key("email") is False
        assert is_sensitive_key("name") is False
        assert is_sensitive_key("count") is False
