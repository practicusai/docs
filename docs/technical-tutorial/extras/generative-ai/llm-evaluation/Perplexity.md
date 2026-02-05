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

# Perplexity Evaluation

This short example demonstrates how to compute **Perplexity** using the shared Practicus AI `eval_metrics` helpers.

Perplexity measures how well a language model predicts text — **lower is better**.

Unlike BLEU / ROUGE / METEOR, Perplexity does **not** require reference texts.



## 1. Import the metric
The `PerplexityMetric` uses a causal LM (default: `gpt2`) to compute token-level negative log-likelihood.

```python
from eval_metrics import PerplexityMetric

# Initialize metric
perp = PerplexityMetric(model_name="gpt2")

perp

```

## 2. Define some generated text
We evaluate Perplexity on **model outputs** (or any text).

```python
predictions = [
    "The quick brown fox jumps over the lazy dog.",
    "Practicus AI helps teams build scalable machine learning systems.",
    "Large language models are transforming enterprise analytics.",
]

predictions

```

## 3. Compute Perplexity
This returns both the **average perplexity** and **per-sample perplexity values**.

```python
result = perp.compute(predictions=predictions, references=None)
result

```

## 4. View results as a table
This is useful for inspecting which generated outputs are harder for the LM to model.

**Lower scores** = better (more predictable).

```python
import pandas as pd

df = pd.DataFrame(
    {
        "text": predictions,
        "perplexity": result.per_sample_scores,
    }
)
df
```

## Summary
- Perplexity evaluates how well an LM predicts the text.
- Unlike BLEU/ROUGE/METEOR, no references are required.
- This same metric utility is used by Practicus AI model hosting to automatically compute and log evaluation metrics.



---

**Previous**: [Meteor](METEOR.md) | **Next**: [Milvus Embedding And LangChain > Milvus Chain](../milvus-embedding-and-langchain/milvus-chain.md)
