---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

# Evaluating LLM Outputs with BLEU

This notebook gives a small, self-contained introduction to using **BLEU** to evaluate large language model (LLM) outputs.

**BLEU** (Bilingual Evaluation Understudy) is one of the classic metrics for evaluating machine translation and other text generation tasks. It compares:

- A **candidate** sentence or document (LLM output)
- One or more **reference** sentences or documents (usually human-written)

BLEU works by:

- Counting overlapping **n-grams** (contiguous word sequences) between candidate and references
- Combining multiple n-gram precisions (typically 1-gram, 2-gram, 3-gram, 4-gram)
- Applying a **brevity penalty** if the candidate is too short

BLEU scores are usually between **0** (no overlap) and **1** (perfect match). In practice, typical scores are somewhere in between, and relative comparisons between models are more important than absolute values.



## Setup

We will use the implementation from **NLTK** (`nltk.translate.bleu_score`).

High-level steps:

1. Install and import NLTK
2. Tokenize reference and candidate sentences
3. Use `sentence_bleu` for individual examples and `corpus_bleu` for batches


```python
from __future__ import annotations

from typing import Sequence

import nltk
from nltk.translate import bleu_score

# Download tokenizer data if needed
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

def simple_tokenize(text: str) -> list[str]:
    """Very simple tokenization helper using whitespace splitting.

    For real evaluations, you might want a more robust tokenizer, but the
    important thing is to use the same tokenization for references and candidates.
    """
    return text.split()

```

## Tiny Example: One Candidate vs One Reference

Consider a simple example where the candidate and reference are identical:

- Reference: `"she read the book because she was interested in world history"`
- Candidate: `"she read the book because she was interested in world history"`

We expect a **high** BLEU score because the sentences match exactly.


```python
reference_text: str = "she read the book because she was interested in world history"
candidate_text: str = "she read the book because she was interested in world history"

reference_tokens: list[str] = simple_tokenize(reference_text)
candidate_tokens: list[str] = simple_tokenize(candidate_text)

# sentence_bleu expects a list of reference sentences, each a list of tokens
score_same: float = bleu_score.sentence_bleu(
    [reference_tokens],
    candidate_tokens,
)

print("Reference:", reference_text)
print("Candidate:", candidate_text)
print(f"BLEU (identical sentences): {score_same:.4f}")

```

Now change the word order while keeping the meaning similar:

- Reference: `"she read the book because she was interested in world history"`
- Candidate: `"she was interested in world history because she read the book"`

The meaning is almost the same, but the word order is different. BLEU is sensitive to n-gram order, so we expect a **lower** score compared to the identical case.


```python
candidate_reordered_text: str = "she was interested in world history because she read the book"
candidate_reordered_tokens: list[str] = simple_tokenize(candidate_reordered_text)

score_reordered: float = bleu_score.sentence_bleu(
    [reference_tokens],
    candidate_reordered_tokens,
)

print("Reference:", reference_text)
print("Candidate (reordered):", candidate_reordered_text)
print(f"BLEU (reordered sentence): {score_reordered:.4f}")

```

## Sentence-Level vs Corpus-Level BLEU

BLEU was originally designed as a **corpus-level** metric. That is:

- `sentence_bleu` computes BLEU for a single candidate sentence with one or more references.
- `corpus_bleu` computes BLEU across many candidate–reference pairs at once.

Corpus-level BLEU is not just the average of sentence-level scores. Instead it accumulates n-gram counts across the whole dataset and then computes a single score. This tends to be more stable and is usually what papers report.


```python
# Small corpus with two sentences that match perfectly
references_corpus: list[list[list[str]]] = [
    [simple_tokenize("she read the book because she was interested in world history")],
    [simple_tokenize("the book she read was about modern civilizations")],
]

candidates_corpus: list[list[str]] = [
    simple_tokenize("she read the book because she was interested in world history"),
    simple_tokenize("the book she read was about modern civilizations"),
]

corpus_score: float = bleu_score.corpus_bleu(
    list_of_references=references_corpus,
    hypotheses=candidates_corpus,
)

print(f"Corpus-level BLEU for two perfectly matching sentences: {corpus_score:.4f}")

```

## Controlling n-grams with `weights`

BLEU combines the precision of multiple n-gram lengths. In NLTK, this is controlled by the `weights` parameter:

- `weights=(1.0, 0.0, 0.0, 0.0)` → only 1-grams (BLEU-1)
- `weights=(0.0, 1.0, 0.0, 0.0)` → only 2-grams (BLEU-2)
- `weights=(0.25, 0.25, 0.25, 0.25)` → standard 1–4 gram BLEU with equal weight (default)

By examining BLEU scores for different n-gram lengths, you can get a sense of how well the model is doing on local word choice (unigrams) vs. longer phrase structure (higher-order n-grams).


```python
reference_for_weights: list[str] = simple_tokenize(
    "she was interested in world history because she read the book"
)
candidate_for_weights: list[str] = simple_tokenize(
    "she read the book because she was interested in world history"
)

bleu_1gram: float = bleu_score.sentence_bleu(
    [reference_for_weights],
    candidate_for_weights,
    weights=(1.0, 0.0, 0.0, 0.0),
)

bleu_2gram: float = bleu_score.sentence_bleu(
    [reference_for_weights],
    candidate_for_weights,
    weights=(0.0, 1.0, 0.0, 0.0),
)

bleu_3gram: float = bleu_score.sentence_bleu(
    [reference_for_weights],
    candidate_for_weights,
    weights=(0.0, 0.0, 1.0, 0.0),
)

bleu_4gram: float = bleu_score.sentence_bleu(
    [reference_for_weights],
    candidate_for_weights,
    weights=(0.0, 0.0, 0.0, 1.0),
)

print(f"BLEU-1 (unigrams only): {bleu_1gram:.4f}")
print(f"BLEU-2 (bigrams only):  {bleu_2gram:.4f}")
print(f"BLEU-3 (trigrams only): {bleu_3gram:.4f}")
print(f"BLEU-4 (4-grams only):  {bleu_4gram:.4f}")

```

## Helper Function for LLM Evaluation Pipelines

In a real LLM evaluation workflow, you often have:

- A list of **reference texts** (one per input)
- A list of **candidate texts** (model outputs)

Below is a small helper that computes **corpus-level BLEU** for such a batch. It assumes a single reference per candidate for simplicity (you can extend it to multiple references if you have them).


```python
def compute_corpus_bleu(
    references: Sequence[str],
    candidates: Sequence[str],
    weights: tuple[float, float, float, float] = (0.25, 0.25, 0.25, 0.25),
) -> float:
    """Compute corpus-level BLEU for a list of reference and candidate texts.

    - `references`: human-written target texts, one per example
    - `candidates`: model outputs, same length and order as `references`
    """
    if len(references) != len(candidates):
        raise ValueError("references and candidates must have the same length")

    # Convert to the format expected by corpus_bleu:
    # list_of_references: list of list of reference sentences (tokenized)
    # hypotheses: list of candidate sentences (tokenized)
    list_of_references: list[list[list[str]]] = [
        [simple_tokenize(ref)] for ref in references
    ]
    hypotheses: list[list[str]] = [
        simple_tokenize(candidate) for candidate in candidates
    ]

    score: float = bleu_score.corpus_bleu(
        list_of_references=list_of_references,
        hypotheses=hypotheses,
        weights=weights,
    )
    return score


# Example usage with a small batch
batch_references: list[str] = [
    "she read the book because she was interested in world history",
    "the book she read was about modern civilizations",
]

batch_candidates: list[str] = [
    "she read the book because she was interested in world history",
    "the book she read was about modern civilizations",
]

batch_bleu: float = compute_corpus_bleu(
    references=batch_references,
    candidates=batch_candidates,
)

print(f"Corpus-level BLEU for the small batch: {batch_bleu:.4f}")

```

## Summary

- **BLEU** is a classic metric for evaluating text generation, especially machine translation.
- It measures **n-gram precision** between candidate and reference text, with a brevity penalty for very short candidates.
- You can compute BLEU at the **sentence level** (`sentence_bleu`) or **corpus level** (`corpus_bleu`).
- The `weights` parameter controls which n-grams are considered and how they are combined.
- BLEU is straightforward to compute with NLTK and can be integrated into LLM evaluation pipelines alongside other metrics such as ROUGE, METEOR, BERTScore, and BLEURT.

BLEU is best used as one signal among several metrics and human evaluations, rather than as the only measure of quality.



---

**Previous**: [Rogue](ROGUE.md) | **Next**: [Bleurt](BLEURT.md)
