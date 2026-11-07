# Architecture

`language-detect-lite` implements document language identification using the Cavnar & Trenkle (1994) n-gram frequency method.

## Data Pipeline

1. **Text Normalization**: Input text is normalized using Unicode `NFKC` and case-folded.
2. **Tokenization & Padding**: Non-letter characters (or digit runs) are stripped or treated as delimiters. Each word is padded with leading and trailing spaces (`" word "`).
3. **Trigram Generation**: Overlapping 3-character substrings are counted and sorted descending by frequency, with alphabetical tie-breaking.
4. **Profile Matching**: Up to `top` (default 300) trigrams form the profile. For a target text, out-of-place distance computes difference in ranks compared to language profiles.
5. **Scoring**: Scores are normalized to `[0.0, 1.0]` where higher scores indicate stronger similarity.

## Resource Bundling

Bundled language texts (`en`, `es`, `fr`, `de`, `pt`, `it`) are stored as plain text files under `src/language_detect_lite/data/` and loaded lazily via `importlib.resources` and `functools.cache`.
