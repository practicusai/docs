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

# Evaluating LLM Outputs with METEOR

This notebook gives a small, self-contained introduction to using **METEOR** to evaluate large language model (LLM) outputs.

METEOR stands for **Metric for Evaluation of Translation with Explicit ORdering**. It was originally introduced for machine translation, but it is also useful for other text generation tasks such as:

- Text summarization
- Paraphrase generation
- Dialogue / chatbot responses

Unlike some older metrics that focus mainly on **precision** ("how many predicted words are correct"), METEOR combines **precision** and **recall** and also:

- Can match **stems** (e.g., "run", "running", "ran")
- Can match **synonyms** (e.g., "quick" vs. "fast") depending on configuration
- Includes **penalties** for bad word order and fragmented matches

The final METEOR score is a single number between **0** and **1**, where **1** indicates a perfect match between candidate text and reference text (according to METEOR’s alignment and penalty rules).



## How METEOR Works (Conceptual)

At a high level, METEOR follows these steps:

1. **Word matching and alignment**
   - Attempt to match words between candidate and reference using:
     - Exact matches
     - Stemming (matching root forms of words)
     - Synonyms (if resources such as WordNet are used)
   - Build an alignment that links each matched word in the candidate to a word in the reference.

2. **Compute precision and recall**
   - **Precision** = (aligned words) / (total words in candidate)
   - **Recall** = (aligned words) / (total words in reference)
   - Combine these into a harmonic mean (an F-like score).

3. **Apply penalties**
   - Penalize **fragmentation**: if matching words in the candidate are scattered across many separate chunks, the score is reduced.
   - Penalize **ordering problems**: if the overall word order differs a lot from the reference.

4. **Final METEOR score**
   - Adjust the harmonic mean of precision and recall using the penalty terms to obtain the final METEOR score.

In practice, we usually do not implement all these details manually. Instead, we rely on a library implementation that encodes the original paper’s design choices.



## Small Intuition Example

Consider the following sentences:

- Reference: `"A fast brown fox leaps over a lazy dog."`
- Candidate: `"The quick brown fox jumps over the lazy dog."`

Intuitively, these two sentences have nearly the same meaning:

- "fast" vs. "quick" → synonyms
- "leaps" vs. "jumps" → similar meaning (often matched via stemming or synonymy)
- Word order is very similar

A good metric should give this pair a **high** score, even though the words are not all exact matches. METEOR can do this by considering stems and synonyms in its alignment step, and then combining precision, recall, and penalties into a single value.

In the next cells, we will use the implementation from **NLTK** (`nltk.translate.meteor_score`) to compute METEOR scores for such examples.


```python
# If running in a fresh environment, you may need to install NLTK once:
# !pip install nltk

from nltk.translate.meteor_score import meteor_score

reference_sentence: str = "A fast brown fox leaps over a lazy dog"
candidate_sentence: str = "The quick brown fox jumps over the lazy dog"

# meteor_score expects a list of reference sentences and one candidate
score: float = meteor_score([
    reference_sentence
], candidate_sentence)

print(f"Reference: {reference_sentence}")
print(f"Candidate: {candidate_sentence}")
print(f"METEOR score: {score:.4f}")

```

### Notes on the NLTK Implementation

- `meteor_score` can take **multiple references** (a list of strings) and a single candidate.
- Inputs can be raw strings; NLTK will tokenize them internally. You can also pass tokenized lists if you want more control.
- The score is a single float in \[0, 1]. Higher is better.

Next, we will move from a single pair of sentences to a small batch of examples, which is closer to how you would evaluate an LLM on a test set.



## Using METEOR for a Small Batch of LLM Outputs

In a typical LLM evaluation workflow, you have:

- A list of **reference texts** (e.g., human-written summaries or target responses)
- A list of **model outputs** (e.g., LLM-generated summaries or replies)

Each reference and prediction pair corresponds to the same input example (same conversation, same document, etc.).

Below we:

1. Define a small batch of references and candidate outputs.
2. Compute METEOR for each pair.
3. Aggregate the scores (simple average) to get a single batch-level metric.


```python
from typing import Sequence

def compute_meteor_for_batch(
    references: Sequence[str],
    candidates: Sequence[str],
) -> dict[str, float]:
    """Compute METEOR scores for a batch of (reference, candidate) pairs.

    Returns a dictionary with per-example scores and the mean score.
    """
    if len(references) != len(candidates):
        raise ValueError("references and candidates must have the same length")

    per_example_scores: list[float] = []

    for reference_text, candidate_text in zip(references, candidates):
        # meteor_score expects a list of references for each candidate
        example_score: float = meteor_score([
            reference_text
        ], candidate_text)
        per_example_scores.append(example_score)

    if per_example_scores:
        mean_score: float = sum(per_example_scores) / len(per_example_scores)
    else:
        mean_score = 0.0

    return {
        "mean_meteor": mean_score,
        "per_example_scores": per_example_scores,
    }


# Toy batch: references and LLM outputs
batch_references: list[str] = [
    "The system experienced a short outage due to a database failure but has now fully recovered.",
    "The model summarizes customer feedback to highlight common complaints and feature requests.",
    "The research paper introduces a new method for training language models more efficiently.",
]

batch_candidates: list[str] = [
    "A brief outage occurred because the database failed, but the service is now completely restored.",
    "The model creates a summary of user comments, focusing on frequent issues and requested features.",
    "The article presents a new approach that makes training language models more efficient.",
]

meteor_results = compute_meteor_for_batch(
    references=batch_references,
    candidates=batch_candidates,
)

print("Per-example METEOR scores:")
for idx, value in enumerate(meteor_results["per_example_scores"]):
    print(f"  Example {idx}: {value:.4f}")

print(f"\nMean METEOR over batch: {meteor_results['mean_meteor']:.4f}")

```

## Integrating METEOR into an LLM Evaluation / Monitoring Pipeline

In a more complete system, the flow often looks like this:

1. **Collect evaluation dataset**
   - Each row contains input text, a human reference output, and possibly metadata (task type, domain, difficulty, etc.).

2. **Generate model outputs**
   - For each input, call the LLM (API or local model) and store its response.

3. **Compute METEOR**
   - Use a function like `compute_meteor_for_batch(...)` to get per-example and mean scores.
   - Optionally store per-example scores to analyze outliers or task subgroups.

4. **Log & visualize**
   - Log metrics such as mean METEOR (and possibly BLEU, ROUGE, etc.) across evaluation runs.
   - Visualize them over time or across model versions (e.g., in Grafana or a custom dashboard).

5. **Compare variants**
   - Compare METEOR scores for different prompt templates, fine-tuned models, or decoding strategies.

METEOR is typically used alongside other metrics and human evaluation. It is helpful because it:

- Balances precision and recall
- Can handle stems and synonyms
- Penalizes bad word order and fragmented matches

All of these make it a useful signal when you want automatic scores that are **closer to human judgment** than simple n-gram precision alone.



## Summary

- **METEOR** is a metric for evaluating machine-generated text (originally translation) that combines precision, recall, and penalties for poor ordering/fragmentation.
- It goes beyond exact string matching by considering **stems** and optionally **synonyms**.
- Scores range from **0** to **1**, where higher is better.
- The **NLTK** implementation (`meteor_score`) provides an easy way to compute METEOR in Python.
- In real LLM systems, METEOR can be computed on full evaluation sets and logged over time as part of your model monitoring stack.

This notebook is intentionally minimal and is meant as a starting point. You can adapt it to your own datasets, LLM endpoints, and evaluation pipelines.



---

**Previous**: [Bertscore](BERTScore.md) | **Next**: [Perplexity](Perplexity.md)
