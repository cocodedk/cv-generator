"""Tests for key derivation for scrambling offsets."""

import hashlib
from backend.cv_generator.scramble import _derive_offsets


class TestDeriveOffsets:
    """Test key derivation for scrambling offsets."""

    def test_deterministic_offset_generation(self):
        """Test that same key produces same offsets."""
        key = "test-key-123"
        offset1 = _derive_offsets(key)
        offset2 = _derive_offsets(key)
        assert offset1 == offset2

    def test_offset_ranges(self):
        """Test that offsets are within valid ranges."""
        key = "test-key"
        alpha_offset, digit_offset = _derive_offsets(key)
        assert 0 <= alpha_offset < 26
        assert 0 <= digit_offset < 10

    def test_offsets_match_manual_sha256(self):
        """Test that offsets match a manual SHA256 derivation."""
        key = "test-key-abc-123"
        digest = hashlib.sha256(key.encode("utf-8")).digest()
        offset = int.from_bytes(digest[:4], "big")
        expected = (offset % 26, offset % 10)
        assert _derive_offsets(key) == expected
