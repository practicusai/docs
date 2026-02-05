---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: practicus
    language: python
    name: python3
---

# Evaluating LLM Outputs with ROUGE

This notebook gives a very small, self-contained introduction to using **ROUGE** to evaluate large language model (LLM) outputs.

We focus on text summarization, but the same idea applies to other generation tasks where you have:

- A **reference** text (often written or approved by a human), and
- A **prediction** text produced by an LLM.

Traditional ML metrics (accuracy, RMSE, etc.) expect fixed-size numeric outputs. LLMs, on the other hand, produce **variable-length text**. ROUGE is one of the classic metrics used to compare *how similar* two pieces of text are, in terms of overlapping words/subsequences.



## ROUGE: High-level Idea

**ROUGE** (Recall-Oriented Understudy for Gisting Evaluation) compares a *candidate* text to a *reference* text and measures how much overlap they have.

Common variants:

- **ROUGE-1**: Overlap of unigrams (single words)
- **ROUGE-2**: Overlap of bigrams (pairs of consecutive words)
- **ROUGE-L**: Overlap based on the Longest Common Subsequence (LCS)

Each ROUGE variant can be reported as:

- **Recall**: How much of the reference is covered by the prediction?
- **Precision**: How much of the prediction matches the reference?
- **F1 score**: Harmonic mean of precision and recall.

Values are usually between **0** and **1**, where a higher value means more overlap (and usually better quality, assuming the reference is good).



## Tiny Manual Example (ROUGE-1)

Consider this toy example:

- Reference summary: `"The weather is cold outside."`
- Model output: `"The weather is cold."`

Tokens (ignoring punctuation and case):

- Reference tokens: `[the, weather, is, cold, outside]`
- Prediction tokens: `[the, weather, is, cold]`

Overlap (unigrams): `[the, weather, is, cold]` → 4 overlapping words.

- ROUGE-1 **recall** = 4 / 5 = 0.8
- ROUGE-1 **precision** = 4 / 4 = 1.0
- ROUGE-1 **F1** = 2 × (precision × recall) / (precision + recall)

In the next cell, we implement this calculation in Python to illustrate what ROUGE-1 is doing conceptually (in practice we usually use a library instead of manual counting).


```python
from collections import Counter
from typing import Iterable

def tokenize_simple(text: str) -> list[str]:
    """Very simple whitespace tokenizer, lowercasing and stripping punctuation.
    This is only for illustration; real ROUGE implementations are more careful.
    """
    punctuation_chars: str = ",.!?:;"  # toy example, not robust
    cleaned: str = text.lower()
    for ch in punctuation_chars:
        cleaned = cleaned.replace(ch, "")
    tokens: list[str] = cleaned.split()
    return tokens

def rouge_1_precision_recall_f1(reference: str, prediction: str) -> dict[str, float]:
    reference_tokens: list[str] = tokenize_simple(reference)
    prediction_tokens: list[str] = tokenize_simple(prediction)

    ref_counts: Counter[str] = Counter(reference_tokens)
    pred_counts: Counter[str] = Counter(prediction_tokens)

    # Count overlapping unigrams (intersection of multisets)
    overlap: int = 0
    for token, pred_count in pred_counts.items():
        overlap += min(pred_count, ref_counts.get(token, 0))

    if len(reference_tokens) == 0 or len(prediction_tokens) == 0:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    recall: float = overlap / len(reference_tokens)
    precision: float = overlap / len(prediction_tokens)

    if precision + recall == 0:
        f1: float = 0.0
    else:
        f1 = 2 * (precision * recall) / (precision + recall)

    return {"precision": precision, "recall": recall, "f1": f1}

reference_example: str = "The weather is cold outside."
prediction_example: str = "The weather is cold."

scores_example = rouge_1_precision_recall_f1(
    reference=reference_example,
    prediction=prediction_example,
)
scores_example

```

## Using Hugging Face `evaluate` for ROUGE

Manually counting overlapping tokens is fine for learning, but for real workloads we use a library.

The [`evaluate`](https://huggingface.co/docs/evaluate/index) library from Hugging Face provides a ready-made ROUGE implementation.

Below we will:

1. Install the `evaluate` library (if needed).
2. Define a small list of **reference summaries** (what humans wrote).
3. Define a list of **model summaries** (what the LLM produced).
4. Compute ROUGE scores.

In a real evaluation pipeline, the references and predictions would typically come from:

- A held-out test set in a dataset; or
- Logs where human reviewers wrote the “ideal” answer and the model answer is stored separately.


```python
# If running in a fresh environment, you may need to install the library once:
# !pip install evaluate

import evaluate
from pprint import pprint

# Load the ROUGE metric implementation
rouge = evaluate.load("rouge")

# Toy example references (human-written)
references: list[str] = [
    "The weather is cold outside today, with strong winds and cloudy skies.",
    "The company reported higher quarterly profits driven by strong online sales.",
    "The movie follows a young hero who must overcome fear to save their village."
]

# Toy example predictions (LLM-generated summaries)
predictions: list[str] = [
    "It is cold and windy outside today, and the sky is cloudy.",
    "The company posted better profits this quarter thanks to online sales.",
    "A young hero conquers fear to protect the village in the movie."
]

results: dict[str, float] = rouge.compute(
    predictions=predictions,
    references=references,
    use_aggregator=True,  # average over all examples
)

print("ROUGE scores (aggregated over all examples):")
pprint(results)

```

You should see a dictionary containing metrics such as:

- `rouge1`  → ROUGE-1 F1 score
- `rouge2`  → ROUGE-2 F1 score
- `rougeL`  → ROUGE-L F1 score
- `rougeLsum` → a variant of ROUGE-L often used for summarization

All of these scores are between 0 and 1. Higher values indicate more overlap between the model output and the reference.



## Plugging This into an LLM Evaluation Workflow

In a real LLM system, the pipeline for automatic ROUGE evaluation often looks like this:

1. **Collect evaluation data**
   - Each item has input text (e.g., an article or conversation), a human-written reference summary, and sometimes metadata like difficulty, domain, etc.

2. **Generate model outputs**
   - For each input, call your LLM (via API or locally) and store the generated summary.

3. **Post-process text** (optional but common)
   - Lowercasing, stripping extra whitespace, removing special tokens, etc.

4. **Compute ROUGE**
   - Pass the list of model outputs and reference summaries to `rouge.compute(...)`.

5. **Monitor over time**
   - Store scores (e.g., in a time series DB) and visualize them in tools like Grafana.
   - Compare different model versions or prompt templates.

In the next cell, we sketch a simple helper function that you can plug into a larger evaluation script. It assumes you already have aligned lists of references and predictions (same length, same order).


```python
from typing import Sequence

def compute_rouge_scores(
    references: Sequence[str],
    predictions: Sequence[str],
) -> dict[str, float]:
    """Compute aggregated ROUGE scores for a list of references and predictions.

    Returns a dict with keys like "rouge1", "rouge2", "rougeL", "rougeLsum".
    """
    if len(references) != len(predictions):
        raise ValueError("references and predictions must have the same length")

    metric = evaluate.load("rouge")
    scores: dict[str, float] = metric.compute(
        predictions=list(predictions),
        references=list(references),
        use_aggregator=True,
    )
    return scores

# Example reuse with the earlier toy data
rouge_scores = compute_rouge_scores(
    references=references,
    predictions=predictions,
)
pprint(rouge_scores)

```

## Summary

- LLMs generate **free-form text**, so we cannot use accuracy/precision/recall on labels directly.
- **ROUGE** compares model output to reference text based on overlapping words or subsequences.
- **ROUGE-1**, **ROUGE-2**, and **ROUGE-L** each capture slightly different notions of similarity.
- The Hugging Face `evaluate` library provides an easy way to compute ROUGE for batches of texts.
- In production, you can log ROUGE scores per model version and track them in your monitoring stack alongside other metrics.

This notebook is deliberately minimal and meant as a starting point. You can adapt it to your own datasets, LLM endpoints, and monitoring tools.



---

**Previous**: [Overview](Overview.md) | **Next**: [Bleu](BLEU.md)
