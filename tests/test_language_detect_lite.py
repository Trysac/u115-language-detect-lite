"""Behavior tests for the public API of language_detect_lite."""

from __future__ import annotations

import pytest

import language_detect_lite


def test_normalize_trims_and_lowercases() -> None:
    assert language_detect_lite.normalize("  Hello World ") == "hello world"


@pytest.mark.parametrize("value", ["", "   ", "\t\n"])
def test_normalize_rejects_blank_input(value: str) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        language_detect_lite.normalize(value)


def test_version_is_semver() -> None:
    parts = language_detect_lite.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
