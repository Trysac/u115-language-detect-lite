# Use Cavnar-Trenkle N-gram Out-of-Place Distance for Dependency-Free Language Detection

Status: accepted (generated, pending human review)

## Context

Lightweight document routing, LLM response verification, and indexing need language identification without heavyweight models, native C dependencies, or external runtime libraries. For paragraph-length text across major languages, the Cavnar and Trenkle (1994) character n-gram ranking method is fast, explainable, and reliable.

## Decision

We implement character trigram profiling with NFKC normalization, letter extraction, word-boundary padding, and out-of-place rank distance bounded to [0.0, 1.0]. Six language profiles (en, es, fr, de, pt, it) are bundled and trained on original prose held out from test cases. Custom profiles can be trained dynamically with input bounds checking.

## Consequences

Provides sub-millisecond, dependency-free language detection with high accuracy on natural text >= 20 characters. Closely related dialects or very short snippets remain out of scope.
