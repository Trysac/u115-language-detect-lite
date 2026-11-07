# language-detect-lite

[![CI](https://github.com/Trysac/u115-language-detect-lite/actions/workflows/ci.yml/badge.svg)](https://github.com/Trysac/u115-language-detect-lite/actions/workflows/ci.yml)

Fast, dependency-free language detection using character trigram profiles and the Cavnar-Trenkle out-of-place distance method (1994). Includes bundled profiles for six major languages (`en`, `es`, `fr`, `de`, `pt`, `it`) and supports custom training.

## Features

- **Zero runtime dependencies**: Pure Python standard library implementation.
- **Cavnar-Trenkle Algorithm**: Character trigram ranking with out-of-place distance.
- **6 Bundled Languages**: English (`en`), Spanish (`es`), French (`fr`), German (`de`), Portuguese (`pt`), and Italian (`it`).
- **Trainable**: Easily create custom profiles using `train()`.
- **Deterministic & Safe**: Bounded memory, scanning limits, and full typing support.
- **CLI Included**: Terminal tool for one-shot text detection and candidate ranking.

## Installation

```bash
pip install trysac-language-detect-lite
```

## Usage

```python
import language_detect_lite as ldl

text = "The weather is very nice today and we are going to the beach with our friends"
print(ldl.detect(text))  # 'en'

scores = ldl.rank("Bonjour le monde")
print(scores[0])  # ('fr', ...)
```

## CLI Usage

```bash
# Detect language of text from stdin
echo "Das Wetter ist heute sehr schön" | python -m language_detect_lite
# Output: de

# Rank all language candidates with scores
python -m language_detect_lite --rank sample.txt
```

## License

MIT
