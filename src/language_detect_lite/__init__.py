"""Dependency-free language detection with character trigram profiles (Cavnar-Trenkle)."""

from __future__ import annotations

import functools
import importlib.resources
import logging
import re
import unicodedata
from collections import Counter
from collections.abc import Mapping
from typing import Literal

__all__ = [
    "LanguageError",
    "Profiles",
    "__version__",
    "detect",
    "rank",
    "train",
]

__version__ = "0.1.0"

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

ErrorCode = Literal["empty_sample", "invalid_code", "input_too_large", "invalid_option"]

MAX_INPUT_CHARS: int = 1_000_000
DEFAULT_TOP_TRIGRAMS: int = 300
DEFAULT_MIN_CHARS: int = 20
DEFAULT_MAX_SCAN_CHARS: int = 10_000

CODE_PATTERN = re.compile(r"^[a-z]{2,3}$")
NON_LETTER_PATTERN = re.compile(r"[^\w\s]|_|[\d\s]+")


class LanguageError(ValueError):
    """Base exception raised for language detection errors."""

    def __init__(self, code: ErrorCode, message: str | None = None) -> None:
        self.code: ErrorCode = code
        msg = message or f"Language detection error: {code}"
        # Limit length to at most 200 chars
        super().__init__(msg[:200])


Profiles = Mapping[str, tuple[str, ...]]


def _extract_trigrams(text: str, top: int) -> tuple[str, ...]:
    """Extract ranked character trigrams from text according to Cavnar & Trenkle."""
    normalized = unicodedata.normalize("NFKC", text).casefold()
    counts: Counter[str] = Counter()

    # Split into words by replacing any sequence of non-letters with a space
    # Letters are characters with unicode category starting with 'L'
    words: list[str] = []
    current_word: list[str] = []
    for char in normalized:
        if unicodedata.category(char).startswith("L"):
            current_word.append(char)
        else:
            if current_word:
                words.append("".join(current_word))
                current_word = []
    if current_word:
        words.append("".join(current_word))

    for word in words:
        padded = f" {word} "
        if len(padded) >= 3:
            for i in range(len(padded) - 2):
                counts[padded[i : i + 3]] += 1

    # Rank by count descending, then trigram ascending
    sorted_trigrams = sorted(counts.keys(), key=lambda tg: (-counts[tg], tg))
    return tuple(sorted_trigrams[:top])


def train(samples: Mapping[str, str], *, top: int = DEFAULT_TOP_TRIGRAMS) -> Profiles:
    """Train language profiles from a mapping of language codes to sample texts.

    Args:
        samples: Mapping of language codes (^[a-z]{2,3}$) to text samples.
        top: Number of top trigrams to keep per profile (must be >= 1).

    Returns:
        Profiles mapping language codes to ranked trigram tuples.
    """
    if top < 1:
        raise LanguageError("invalid_option", "top must be at least 1")

    profiles: dict[str, tuple[str, ...]] = {}
    for code, sample in samples.items():
        if not isinstance(code, str) or not CODE_PATTERN.match(code):
            raise LanguageError("invalid_code", f"Invalid language code: {code}")
        if len(sample) > MAX_INPUT_CHARS:
            raise LanguageError("input_too_large", "Sample text exceeds maximum allowed size")
        if not sample.strip():
            raise LanguageError("empty_sample", f"Sample text for code '{code}' is empty")

        trigrams = _extract_trigrams(sample, top)
        if not trigrams:
            raise LanguageError("empty_sample", f"Sample text for code '{code}' has no letters")
        profiles[code] = trigrams

    return profiles


@functools.cache
def _get_bundled_profiles() -> Profiles:
    """Load and build default bundled profiles for en, es, fr, de, pt, and it."""
    bundled_codes = ("en", "es", "fr", "de", "pt", "it")
    samples: dict[str, str] = {}
    pkg_data = importlib.resources.files("language_detect_lite.data")
    for code in bundled_codes:
        file_path = pkg_data.joinpath(f"{code}.txt")
        text = file_path.read_text(encoding="utf-8")
        # Remove comment lines starting with '#'
        cleaned_lines = [line for line in text.splitlines() if not line.startswith("#")]
        samples[code] = "\n".join(cleaned_lines)
    return train(samples, top=DEFAULT_TOP_TRIGRAMS)


def rank(
    text: str,
    *,
    profiles: Profiles | None = None,
    max_scan_chars: int = DEFAULT_MAX_SCAN_CHARS,
) -> list[tuple[str, float]]:
    """Rank all profile languages by similarity to the input text.

    Args:
        text: Input text to evaluate.
        profiles: Custom profiles mapping, or None to use bundled profiles.
        max_scan_chars: Maximum characters to inspect from input text.

    Returns:
        List of tuples `(language_code, score)` sorted by score descending,
        with ties broken by language code ascending. Score is in [0.0, 1.0].
    """
    if len(text) > MAX_INPUT_CHARS:
        raise LanguageError("input_too_large", "Input text exceeds maximum allowed size")
    if max_scan_chars < 1:
        raise LanguageError("invalid_option", "max_scan_chars must be at least 1")

    active_profiles = profiles if profiles is not None else _get_bundled_profiles()
    if not active_profiles:
        return []

    scanned_text = text[:max_scan_chars]
    # Text profile is extracted with up to DEFAULT_TOP_TRIGRAMS (300)
    text_profile = _extract_trigrams(scanned_text, top=DEFAULT_TOP_TRIGRAMS)
    if not text_profile:
        # No trigrams could be formed (e.g. no letters or short)
        # Return all languages with score 0.0, sorted by code
        return sorted([(code, 0.0) for code in active_profiles], key=lambda item: item[0])

    n = DEFAULT_TOP_TRIGRAMS
    results: list[tuple[str, float]] = []

    for code, lang_trigrams in active_profiles.items():
        lang_rank_map = {tg: idx for idx, tg in enumerate(lang_trigrams)}
        distance = 0
        for r_t, tg in enumerate(text_profile):
            if tg in lang_rank_map:
                distance += abs(r_t - lang_rank_map[tg])
            else:
                distance += n

        max_dist = n * len(text_profile)
        score = 1.0 - (distance / max_dist)
        # Ensure float bounds within [0.0, 1.0]
        score = max(0.0, min(1.0, score))
        results.append((code, round(score, 6)))

    # Sort descending by score, tie-breaking by code ascending
    results.sort(key=lambda item: (-item[1], item[0]))
    return results


def detect(
    text: str,
    *,
    profiles: Profiles | None = None,
    min_chars: int = DEFAULT_MIN_CHARS,
    max_scan_chars: int = DEFAULT_MAX_SCAN_CHARS,
) -> str | None:
    """Detect the primary language of the given text.

    Args:
        text: Input text to detect.
        profiles: Custom profiles or None to use default bundled profiles.
        min_chars: Minimum number of letters required in scanned prefix.
        max_scan_chars: Maximum characters to inspect from input text.

    Returns:
        Best language code or None if letter count is below min_chars.
    """
    if len(text) > MAX_INPUT_CHARS:
        raise LanguageError("input_too_large", "Input text exceeds maximum allowed size")
    if min_chars < 0:
        raise LanguageError("invalid_option", "min_chars cannot be negative")
    if max_scan_chars < 1:
        raise LanguageError("invalid_option", "max_scan_chars must be at least 1")

    scanned_text = text[:max_scan_chars]
    letter_count = sum(1 for c in scanned_text if c.isalpha())
    if letter_count < min_chars:
        return None

    rankings = rank(text, profiles=profiles, max_scan_chars=max_scan_chars)
    if not rankings:
        return None
    return rankings[0][0]
