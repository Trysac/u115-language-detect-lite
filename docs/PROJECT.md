# Project record

## Objective

Dependency-free language detection with character trigram profiles and the Cavnar-Trenkle out-of-place distance, six bundled languages and trainable custom profiles

## Scope

- In scope: the public API documented in [README.md](../README.md), typed and tested.
- Out of scope: anything that needs runtime dependencies or I/O without an accepted ADR.

## Timeline

| Date | Event |
|---|---|
| 2026 | Repository created from the factory utility template. |

## Effort metrics

Measured values only; a value that has not been measured stays "pending measurement".

| Metric | Value |
|---|---|
| Tokens (input / output) | 457197 / 13147 |
| Hours (human) | pending measurement |
| Cost (USD) | 0.0997 |

## Factory run u115 (measured from API usage)

| Phase | Model | Batch | Input | Output | Cache write | Cache read | Cost (USD) |
|---|---|---|---|---|---|---|---|
| generation | gemini-3.8-flash | yes | 4078 | 9186 | 0 | 0 | 0.0188 |
| fix-1 | gemini-3.1-flash-lite | no | 13052 | 335 | 0 | 0 | 0.0038 |
| fix-2 | gemini-3.1-flash-lite | no | 12729 | 197 | 0 | 4032 | 0.0036 |
| fix-3 | gemini-3.1-flash-lite | no | 13285 | 195 | 0 | 2018 | 0.0037 |
| fix-4 | gemini-3.1-flash-lite | no | 18152 | 1043 | 0 | 14188 | 0.0065 |
| audit | gemini-3.1-flash-lite | no | 62668 | 330 | 0 | 150042 | 0.0199 |
| docs | gemini-3.1-flash-lite | no | 162953 | 1861 | 0 | 0 | 0.0435 |

Total: $0.0997. Prices: Anthropic list prices.
