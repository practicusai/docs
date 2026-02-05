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

# LLM Evaluation Metrics with Practicus AI

This example documents how we:

1. **Evaluate LLM outputs** using standard text-generation metrics:
   - BLEU
   - ROUGE
   - METEOR
   - BERTScore
   - Perplexity
2. **Test different metrics interactively** (e.g. METEOR) using a shared Python helper library.
3. **Expose the same logic as Practicus AI APIs** so any hosted model can be evaluated automatically.
4. **Push metric results to our observability system** (e.g. Prometheus / ClickHouse).
5. **Visualize trends in Grafana**.

The key idea: we maintain **one reusable metrics library** and reuse it from:

- Testing and design UI
- Practicus AI model-hosting pipelines for automated evaluation
- Background jobs that publish metrics for Grafana


### Automated visualization of LLM Evaluations

![LLM Eval](img/llm_eval.png)


## 1. Environment & Dependencies

The metrics helpers live in a small Python package called `eval_metrics` (in the Practicus AI repo).
It provides implementations of BLEU, ROUGE, METEOR, BERTScore and Perplexity.

Required third-party libraries:

- `sacrebleu` – BLEU
- `rouge-score` – ROUGE
- `nltk` – METEOR
- `bert-score` – BERTScore
- `transformers`, `torch` – Perplexity (via causal LM, e.g. `gpt2`)
- `Design UI` – for the interactive UI (optional for this notebook)

Install (only once per environment):


## 2. Using the Shared Metric Utilities

The `eval_metrics` package provides a small abstraction:

- `MetricResult` – container for a metric result (`name`, `score`, `per_sample_scores`, `details`).
- `TextGenMetric` – protocol/interface for all metrics.
- `get_default_metric_registry()` – returns a dictionary of metric instances keyed by name.

This section shows how a user (or developer) can **experiment with different metrics** such as METEOR, using the same functions that are later called from Practicus APIs and background jobs.



We will define a small test set with **reference texts** (ground truth) and **model outputs** (predictions).
These are the same kinds of inputs the test UI uses.

### References
```text
The cat is sitting on the mat.
Large language models can generate human-like text.
Practicus AI helps teams deploy AI faster.
```

### Predictions

```text
A cat sits on the mat.
Big language models are able to generate text similar to humans.
Practicus AI enables teams to ship AI solutions more quickly.
```    


### 2.1 Example: Compute METEOR

Here we use the **METEOR** implementation from `eval_metrics`. This is the same code used by:

- the UI (for interactive evaluation), and
- backend jobs (for automated evaluation of hosted models).



`MetricResult.score` is the **average METEOR score** over all examples.
`MetricResult.per_sample_scores` contains one score per (prediction, reference) pair.

We can visualize per-sample results or sort examples by their score if needed.



### 2.2 Trying Other Metrics (BLEU, ROUGE, BERTScore, Perplexity)

The same pattern works for all other metrics. The only difference is that **Perplexity** does not use references – it only looks at the generated text.



This interactive experimentation is the **same logic** that the UI app exposes in a no-code UI.
Users can paste texts and choose a metric from a dropdown; the app simply calls these helper classes under the hood.



## 3. Exposing Metrics as Practicus AI APIs

In production, we expose the metrics as an API endpoint in Practicus AI.

Any client (Practicus UI, Airflow task, or notebook) can now call `/evaluate-metric` to compute BLEU/ROUGE/METEOR/BERTScore/Perplexity for a given batch of examples.


## 4. Integrating with Practicus AI Model Hosting

A typical evaluation flow for a hosted model:

1. **Prepare an evaluation dataset** (references, prompts, expected answers) in a table or file.
2. **Call the hosted model** using Practicus AI's standard prediction API.
3. **Collect model outputs** for each test example.
4. **Call the `/evaluate-metric` API** (or directly the metric helpers) with the predictions + references.
5. **Store metric results** in an observability backend (Prometheus / ClickHouse / other TSDB).
6. **Visualize metrics in Grafana** for non-technical stakeholders.

A simplified pseudo-code implementation for an internal evaluation job is shown below.



## 5. Pushing Metrics to the Observability System

Once we have numeric scores for a model + dataset, we publish them to an observability backend.

Common patterns:

- **Prometheus / Pushgateway**: expose `llm_bleu_score`, `llm_meteor_score`, etc.
- **ClickHouse / Postgres**: store evaluation runs in a table for ad-hoc analytics.

Example (conceptual) Prometheus Pushgateway integration for BLEU and METEOR:



With this in place, metrics like `llm_bleu_score{model="example-model", dataset="demo-dataset"}`
become available in Prometheus and can be queried from Grafana.



## 6. Visualizing in Grafana

Finally, Grafana dashboards present these metrics in a way that non-technical users can monitor **LLM quality over time without writing code**.

Typical dashboard elements:

- **Stat panel**: current BLEU (or METEOR / BERTScore) for selected model + dataset.
- **Time-series panel**: metric over time per model (e.g. compare `gpt4_32k` vs `llama3_70b`).
- **Table**: recent evaluation runs with timestamps, model, dataset, and metric values.
- **Filters**: Grafana variables for `model`, `dataset`, `environment` (prod/staging).

Example Prometheus queries used by Grafana panels:

- `llm_bleu_score{model="$model", dataset="$dataset", env="prod"}`
- `llm_meteor_score{model="$model", dataset="$dataset", env="prod"}`
- `llm_bertscore_score{model="$model", dataset="$dataset", env="prod"}`

With this pipeline:

1. **Developers and data scientists** experiment with metrics in notebooks or the UI page.
2. The same metric helpers run as **Practicus AI APIs** and background jobs.
3. Evaluations are pushed to the observability stack automatically.
4. **Grafana** provides a no-code monitoring experience for stakeholders.

This closes the loop from **local experimentation** to **production monitoring** for LLM evaluation.



---

**Previous**: [Langflow Streamlit Hosting](../llm-apps/langflow-llm-apphost/langflow-streamlit-hosting.md) | **Next**: [Rogue](ROGUE.md)
