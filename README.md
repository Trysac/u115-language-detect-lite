# language-detect-lite

[![PyPI version](https://img.shields.io/pypi/v/trysac-language-detect-lite)](https://pypi.org/project/trysac-language-detect-lite/)
[![License: MIT](https://img.shields.io/pypi/l/trysac-language-detect-lite)](LICENSE)
[![CI](https://github.com/Trysac/u115-language-detect-lite/actions/workflows/ci.yml/badge.svg)](https://github.com/Trysac/u115-language-detect-lite/actions/workflows/ci.yml)

Dependency-free language detection with character trigram profiles and the Cavnar-Trenkle out-of-place distance, six bundled languages and trainable custom profiles

## Problem

Describe in two or three sentences the concrete problem this utility solves, who hits it, and what
they do today without it. Replace this paragraph when the first real feature lands.

## Install

```sh
pip install trysac-language-detect-lite
# or
uv add trysac-language-detect-lite
```

Requires Python 3.10 or newer. No runtime dependencies.

## Usage

```python
import language_detect_lite

# normalize() trims surrounding whitespace and lower-cases the text.
print(language_detect_lite.normalize("  Hello World "))  # -> "hello world"

# Blank input is rejected explicitly instead of returning an empty string.
try:
    language_detect_lite.normalize("   ")
except ValueError as exc:
    print(f"rejected: {exc}")
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) and [decisions](docs/decisions/)
- [Testing](docs/TESTING.md) and [security](docs/SECURITY.md)
- [Project record](docs/PROJECT.md) and [stack](docs/STACK.md)
- [Changelog](CHANGELOG.md) and [contributing guide](CONTRIBUTING.md)

## License

[MIT](LICENSE) (c) 2026 Miguel Gomez
