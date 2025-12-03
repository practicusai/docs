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

# Evaluating LLM Outputs with BERTScore

This notebook introduces **BERTScore**, a modern evaluation metric for text generation.

Unlike n-gram-based metrics such as BLEU, ROUGE, or METEOR, BERTScore uses **contextual embeddings** from a pretrained Transformer (e.g., BERT, RoBERTa) to compare:

- A **candidate** text (LLM output)
- A **reference** text (human-written or ground-truth output)

For each token, BERTScore:

1. Embeds tokens using a pretrained model.
2. Computes pairwise cosine similarity between tokens in the candidate and tokens in the reference.
3. Aggregates these similarities into **precision**, **recall**, and **F1** scores.

This allows BERTScore to recognize semantic similarity even when there is little exact token overlap (for example, paraphrases or synonyms).



## Why BERTScore?

Traditional metrics (BLEU, ROUGE, METEOR) rely on n-gram overlap and are sensitive to:

- Exact wording
- Surface tokenization differences
- Word order variations

BERTScore instead compares **meaning** via contextual embeddings. This is especially helpful when models generate:

- Paraphrased text
- Different but semantically equivalent phrases

BERTScore outputs three values (between 0 and 1):

- **Precision**: how well candidate tokens are matched in the reference (similar to classic precision)
- **Recall**: how well reference tokens are covered by candidate tokens
- **F1**: harmonic mean of precision and recall



## Using `evaluate` with BERTScore

We will use the [Hugging Face `evaluate`](https://huggingface.co/docs/evaluate/index) library, which provides a simple wrapper around BERTScore.

High-level steps:

1. Install `evaluate` and `bert-score` (if not already installed).
2. Define reference and candidate sentences.
3. Call `evaluate.load("bertscore")` and compute scores.

You can later plug the same pattern into your LLM evaluation pipeline.


```python
# If running in a fresh environment, you may need to install these once:
# !pip install evaluate bert-score

from typing import Sequence

import evaluate
from pprint import pprint

# Load BERTScore metric
bertscore_metric = evaluate.load("bertscore")

# Example batch: reference vs candidate sentences
references: list[str] = [
    "The system experienced a short outage due to a database failure but has now fully recovered.",
    "The model summarizes customer feedback to highlight common complaints and feature requests.",
    "The research paper introduces a new method for training language models more efficiently."
]

candidates: list[str] = [
    "A brief outage occurred because the database failed, but the service is now completely restored.",
    "The model creates a summary of user comments, focusing on frequent issues and requested features.",
    "The article presents a new approach that makes training language models more efficient."
]

results = bertscore_metric.compute(
    predictions=candidates,
    references=references,
    lang="en",  # language tag for underlying model
)

print("BERTScore raw outputs:")
pprint(results)

# results contains lists of precision, recall, f1 (one value per example)
precisions: list[float] = results["precision"]
recalls: list[float] = results["recall"]
f1_scores: list[float] = results["f1"]

def mean(values: Sequence[float]) -> float:
    return float(sum(values) / len(values)) if values else 0.0

print("\nAggregated (mean) BERTScore over batch:")
print(f"  Precision: {mean(precisions):.4f}")
print(f"  Recall   : {mean(recalls):.4f}")
print(f"  F1       : {mean(f1_scores):.4f}")

```

### Interpreting the Outputs

- BERTScore returns **one precision/recall/F1 triple per example**.
- The example above also computes the **mean** across the batch, which is often used as the main monitoring metric.
- Values close to **1.0** indicate that candidate sentences are very similar in meaning to references.
- Values closer to **0.0** indicate poor semantic overlap.

In practice, you can:

- Track the mean F1 score over time for each model version.
- Slice scores by task, domain, or difficulty.
- Combine BERTScore with other metrics (BLEU, ROUGE, METEOR, human ratings) for a more complete picture.



## Helper Function for Your Evaluation Pipeline

Below is a small helper that you can reuse in your evaluation scripts. It assumes that you already have aligned lists of references and candidates.


```python
def compute_bertscore_batch(
    references: Sequence[str],
    candidates: Sequence[str],
    lang: str = "en",
) -> dict[str, float]:
    """Compute mean BERTScore precision, recall, and F1 for a batch.

    Returns a dictionary with keys: "precision", "recall", "f1".
    """
    if len(references) != len(candidates):
        raise ValueError("references and candidates must have the same length")

    metric = evaluate.load("bertscore")
    scores = metric.compute(
        predictions=list(candidates),
        references=list(references),
        lang=lang,
    )

    precisions_local: list[float] = scores["precision"]
    recalls_local: list[float] = scores["recall"]
    f1_local: list[float] = scores["f1"]

    return {
        "precision": mean(precisions_local),
        "recall": mean(recalls_local),
        "f1": mean(f1_local),
    }

# Quick reuse with earlier toy data
batch_scores = compute_bertscore_batch(
    references=references,
    candidates=candidates,
    lang="en",
)
print("Mean BERTScore batch scores:")
pprint(batch_scores)

```

## Summary

- **BERTScore** uses contextual embeddings to compare candidate and reference texts.
- It outputs **precision**, **recall**, and **F1**, all in \[0, 1].
- It is especially useful when your LLM often produces paraphrased but semantically similar text.
- You can integrate BERTScore into your existing evaluation and monitoring stack alongside BLEU, ROUGE, and METEOR.



---

**Previous**: [Rogue](ROGUE.md) | **Next**: [Bleu](BLEU.md)
