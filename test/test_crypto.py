"""
Tests for core/encryption.py — AES-256-GCM encrypt/decrypt.
"""
import os
import pytest
from cryptography.exceptions import InvalidTag
from core.auth import generate_salt
from core.encryption import encrypt_data, decrypt_data, NONCE_SIZE


PASSWORD = "test-master-key-comrade"


class TestEncryptData:
    def test_returns_bytes(self):
        salt = generate_salt()
        result = encrypt_data(b"hello world", PASSWORD, salt)
        assert isinstance(result, bytes)

    def test_output_longer_than_input(self):
        """Output must contain nonce + ciphertext + GCM tag."""
        salt = generate_salt()
        plaintext = b"secret data"
        result = encrypt_data(plaintext, PASSWORD, salt)
        # nonce (12) + ciphertext (len) + GCM tag (16)
        assert len(result) > len(plaintext) + NONCE_SIZE

    def test_nonce_is_unique_per_call(self):
        """Two encryptions of identical data must produce different ciphertexts."""
        salt = generate_salt()
        data = b"same data every time"
        ct1 = encrypt_data(data, PASSWORD, salt)
        ct2 = encrypt_data(data, PASSWORD, salt)
        assert ct1 != ct2  # different nonces

    def test_encrypts_empty_bytes(self):
        salt = generate_salt()
        result = encrypt_data(b"", PASSWORD, salt)
        assert isinstance(result, bytes)

    def test_encrypts_large_data(self):
        salt = generate_salt()
        large = os.urandom(10 * 1024 * 1024)  # 10 MB
        result = encrypt_data(large, PASSWORD, salt)
        assert len(result) > len(large)


class TestDecryptData:
    def test_round_trip(self):
        """Encrypt then decrypt must recover the original plaintext."""
        salt = generate_salt()
        plaintext = b"the quick brown fox jumps over the lazy dog"
        ciphertext = encrypt_data(plaintext, PASSWORD, salt)
        recovered = decrypt_data(ciphertext, PASSWORD, salt)
        assert recovered == plaintext

    def test_round_trip_binary(self):
        """Round-trip must work on arbitrary binary data."""
        salt = generate_salt()
        plaintext = os.urandom(4096)
        ciphertext = encrypt_data(plaintext, PASSWORD, salt)
        assert decrypt_data(ciphertext, PASSWORD, salt) == plaintext

    def test_wrong_password_raises(self):
        """Decrypting with the wrong password must raise InvalidTag."""
        salt = generate_salt()
        ciphertext = encrypt_data(b"top secret", PASSWORD, salt)
        with pytest.raises(InvalidTag):
            decrypt_data(ciphertext, "wrong-password", salt)

    def test_wrong_salt_raises(self):
        """Decrypting with a different salt must raise InvalidTag."""
        salt1 = generate_salt()
        salt2 = generate_salt()
        ciphertext = encrypt_data(b"secret", PASSWORD, salt1)
        with pytest.raises(InvalidTag):
            decrypt_data(ciphertext, PASSWORD, salt2)

    def test_tampered_ciphertext_raises(self):
        """Any bit flip in the ciphertext must be detected (AEAD integrity)."""
        salt = generate_salt()
        ciphertext = bytearray(encrypt_data(b"sensitive", PASSWORD, salt))
        # Flip a bit in the middle of the ciphertext
        ciphertext[NONCE_SIZE + 4] ^= 0xFF
        with pytest.raises(InvalidTag):
            decrypt_data(bytes(ciphertext), PASSWORD, salt)

    def test_truncated_data_raises(self):
        """Truncated ciphertext must raise (too short to contain a nonce)."""
        with pytest.raises((ValueError, InvalidTag)):
            decrypt_data(b"\x00" * 5, PASSWORD, generate_salt())

    def test_empty_password_round_trip(self):
        """Empty password is consistent (encrypt + decrypt with same empty pw)."""
        salt = generate_salt()
        plaintext = b"test"
        ct = encrypt_data(plaintext, "", salt)
        assert decrypt_data(ct, "", salt) == plaintext

    def test_unicode_password_round_trip(self):
        salt = generate_salt()
        plaintext = b"unicode test"
        pw = "p@$$w0rd🔐"
        ct = encrypt_data(plaintext, pw, salt)
        assert decrypt_data(ct, pw, salt) == plaintext


class TestIntegration:
    def test_multiple_files_independent_salts(self):
        """Each vault entry uses its own salt — cross-decryption must fail."""
        salt_a = generate_salt()
        salt_b = generate_salt()
        ct_a = encrypt_data(b"file A content", PASSWORD, salt_a)
        ct_b = encrypt_data(b"file B content", PASSWORD, salt_b)

        assert decrypt_data(ct_a, PASSWORD, salt_a) == b"file A content"
        assert decrypt_data(ct_b, PASSWORD, salt_b) == b"file B content"

        with pytest.raises(InvalidTag):
            decrypt_data(ct_a, PASSWORD, salt_b)
