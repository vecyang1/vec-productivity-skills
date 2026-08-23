#!/usr/bin/env python3
"""
Unit tests for Google Drive integration in Read-Media-Gemini
"""

import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from chat import extract_drive_file_id, is_drive_url


def test_extract_drive_file_id():
    """Test file ID extraction from various URL formats"""

    # Test full Drive URL
    url1 = "https://drive.google.com/file/d/1ABC123XYZ456/view"
    assert extract_drive_file_id(url1) == "1ABC123XYZ456", "Failed to extract from full URL"

    # Test open URL format
    url2 = "https://drive.google.com/open?id=1ABC123XYZ456"
    assert extract_drive_file_id(url2) == "1ABC123XYZ456", "Failed to extract from open URL"

    # Test direct file ID (25+ chars)
    file_id = "1ABC123XYZ456789012345678"
    assert extract_drive_file_id(file_id) == file_id, "Failed to recognize direct file ID"

    # Test invalid inputs
    assert extract_drive_file_id("") is None, "Should return None for empty string"
    assert extract_drive_file_id("not-a-drive-url") is None, "Should return None for invalid URL"
    assert extract_drive_file_id("short") is None, "Should return None for short string"

    print("✓ All extract_drive_file_id tests passed")


def test_is_drive_url():
    """Test Drive URL detection"""

    # Valid Drive URLs
    assert is_drive_url("https://drive.google.com/file/d/1ABC123XYZ456/view"), "Should detect full Drive URL"
    assert is_drive_url("https://drive.google.com/open?id=1ABC123XYZ456"), "Should detect open URL"
    assert is_drive_url("1ABC123XYZ456789012345678"), "Should detect direct file ID"

    # Invalid inputs
    assert not is_drive_url(""), "Should not detect empty string"
    assert not is_drive_url(None), "Should not detect None"
    assert not is_drive_url("/path/to/local/file.jpg"), "Should not detect local path"
    assert not is_drive_url("https://example.com/file.jpg"), "Should not detect non-Drive URL"
    assert not is_drive_url("short"), "Should not detect short string"

    print("✓ All is_drive_url tests passed")


if __name__ == "__main__":
    test_extract_drive_file_id()
    test_is_drive_url()
    print("\n✓ All Google Drive integration tests passed!")
