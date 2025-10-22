"""Common constants for nicovideo fixture generation."""

from __future__ import annotations

import pathlib

# Test fixtures directories
_BASE_DIR = pathlib.Path(__file__).parent.parent
GENERATED_DIR = _BASE_DIR
GENERATED_FIXTURES_DIR = GENERATED_DIR / "fixtures"
GENERATED_SNAPSHOTS_DIR = GENERATED_DIR / "snapshots"

# Sample test data IDs
SAMPLE_VIDEO_ID = "sm45285955"
SAMPLE_USER_ID = "68461151"
SAMPLE_MYLIST_ID = "78597499"
SAMPLE_SERIES_ID = "527007"
