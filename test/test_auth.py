"""
Tests for core/auth.py — Key derivation and salt generation.
"""
import os
import pytest
from core.auth import derive_key, generate_salt, SCRYPT_N, SCRYPT_R, SCRYPT_P, KEY_LENGTH


class TestGenerateSalt:
    def test_returns_32_bytes(self):
        salt = generate_salt()
        assert isinstance(salt, bytes)
        assert len(salt) == 32

    def test_unique_each_call(self):
        """Two salts must never be equal (with overwhelming probability)."""
        salts = {generate_salt() for _ in range(50)}
        assert len(salts) == 50


class TestDeriveKey:
    def test_returns_32_byte_key(self):
        salt = generate_salt()
        key = derive_key("password123", salt)
        assert isinstance(key, bytes)
        assert len(key) == KEY_LENGTH  # 32 bytes = 256 bits

    def test_same_password_same_salt_deterministic(self):
        salt = generate_salt()
        key1 = derive_key("hunter2", salt)
        key2 = derive_key("hunter2", salt)
        assert key1 == key2

    def test_different_password_different_key(self):
        salt = generate_salt()
        key1 = derive_key("password_A", salt)
        key2 = derive_key("password_B", salt)
        assert key1 != key2

    def test_different_salt_different_key(self):
        """Same password with a different salt must produce a different key."""
        password = "samepassword"
        key1 = derive_key(password, generate_salt())
        key2 = derive_key(password, generate_salt())
        assert key1 != key2

    def test_empty_password_works(self):
        """Empty password is valid input (though insecure) — should not crash."""
        salt = generate_salt()
        key = derive_key("", salt)
        assert len(key) == KEY_LENGTH

    def test_unicode_password(self):
        """Unicode passwords (e.g. emoji, non-ASCII) should be handled."""
        salt = generate_salt()
        key = derive_key("p@$$w0rd🔐", salt)
        assert len(key) == KEY_LENGTH

    def test_scrypt_parameters_are_hardened(self):
        """Ensure production parameters meet minimum hardening standards."""
        assert SCRYPT_N >= 2**14, "N must be at least 2^14 for security"
        assert SCRYPT_R >= 8,     "r should be at least 8"
        assert SCRYPT_P >= 1,     "p must be positive"
