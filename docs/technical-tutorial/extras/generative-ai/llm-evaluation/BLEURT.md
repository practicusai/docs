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

# Evaluating LLM Outputs with BLEURT

This notebook introduces **BLEURT**, a learned evaluation metric for text generation.

BLEURT stands for **Bilingual Evaluation Understudy with Representations from Transformers**. It is a **reference-based**, **neural** metric that:

- Takes a candidate text and a reference text
- Feeds them into a pretrained transformer model
- Outputs a single **quality score** (typically a real number, often normalized into a range like 0–1 or similar)

BLEURT is trained on human-rated examples, so its scores are designed to correlate more closely with **human judgments** than purely heuristic metrics (BLEU, ROUGE, METEOR) in many settings.



## Why BLEURT?

Traditional metrics look at surface form (n-grams, overlaps). BLEURT instead uses a **fine-tuned transformer** to directly learn a mapping from (reference, candidate) pairs to a scalar quality score.

Benefits:

- Can capture subtle semantic differences
- More tolerant of paraphrases and wording variations
- Often correlates better with human ratings, especially on sentence-level evaluations

Trade-offs:

- Heavier computationally than simple lexical metrics
- Needs a specific pretrained checkpoint (e.g., BLEURT-20)
- Requires model downloads and potentially more memory



## Using `evaluate` with BLEURT

We will again use Hugging Face's **`evaluate`** library, which wraps BLEURT checkpoints behind a simple interface.

High-level steps:

1. Install `evaluate` and `bleurt` (first run will download a BLEURT model).
2. Define reference and candidate sentences.
3. Call `evaluate.load("bleurt")` and compute scores.

BLEURT scores are real-valued. Depending on the specific checkpoint, values are often in a range that roughly maps to "worse" vs "better" translation quality; concrete ranges can vary, so relative comparisons (model A vs model B) are often more meaningful than absolute thresholds.


```python
# If running in a fresh environment, you may need to install these once:
# !pip install evaluate bleurt

from typing import Sequence

import evaluate
from pprint import pprint

# Load BLEURT metric
# The first call may download a pretrained BLEURT checkpoint
bleurt_metric = evaluate.load("bleurt")

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

results = bleurt_metric.compute(
    predictions=candidates,
    references=references,
)

print("BLEURT raw outputs:")
pprint(results)

scores: list[float] = results["scores"]

def mean(values: Sequence[float]) -> float:
    return float(sum(values) / len(values)) if values else 0.0

print("\nPer-example BLEURT scores:")
for idx, value in enumerate(scores):
    print(f"  Example {idx}: {value:.4f}")

print(f"\nMean BLEURT over batch: {mean(scores):.4f}")

```

### Interpreting BLEURT Scores

- BLEURT returns one scalar **score** per (reference, candidate) pair.
- Larger values generally correspond to **better quality** according to the learned model.
- Absolute ranges can depend on the specific checkpoint; often you care most about **relative differences**:
  - Compare model versions
  - Compare prompt templates
  - Compare decoding strategies (temperature, top-k, etc.)

In practice you might:

- Compute BLEURT for your evaluation set
- Track the mean score per model version
- Use human evaluation on a subset to calibrate how BLEURT scores map to perceived quality in your domain



## Helper Function for Your Evaluation Pipeline

Below is a helper that wraps BLEURT into a simple function you can call from your evaluation scripts.


```python
def compute_bleurt_batch(
    references: Sequence[str],
    candidates: Sequence[str],
) -> dict[str, float | list[float]]:
    """Compute BLEURT scores for a batch of (reference, candidate) pairs.

    Returns a dictionary with the list of per-example scores and the mean score.
    """
    if len(references) != len(candidates):
        raise ValueError("references and candidates must have the same length")

    metric = evaluate.load("bleurt")
    results_local = metric.compute(
        predictions=list(candidates),
        references=list(references),
    )

    scores_local: list[float] = results_local["scores"]
    return {
        "mean_bleurt": mean(scores_local),
        "per_example_scores": scores_local,
    }

# Quick reuse with earlier toy data
batch_results = compute_bleurt_batch(
    references=references,
    candidates=candidates,
)

print("Computed BLEURT batch results:")
pprint(batch_results)

```

## Summary

- **BLEURT** is a learned evaluation metric built on top of pretrained transformers and fine-tuned using human judgments.
- It outputs a **single scalar score** per example, intended to correlate well with human perception of quality.
- It is more computationally expensive than simple lexical metrics, but often more informative.
- You can combine BLEURT with metrics like BLEU, ROUGE, METEOR, and BERTScore to build a richer evaluation and monitoring suite for your LLM workloads.



---

**Previous**: [Bleu](BLEU.md) | **Next**: [Bertscore](BERTScore.md)
