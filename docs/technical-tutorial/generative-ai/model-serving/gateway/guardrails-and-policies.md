---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Practicus AI Model Gateway Guardrails & Policy Enforcement

Practicus AI provides a policy-aware Large Language Model (LLM) gateway that makes it easy to enforce organizational security, compliance, and ethics requirements at the prompt and response layer.

This document focuses on how to:

- define reusable guardrails for input and output validation,
- plug them into the gateway configuration,
- combine them with model-level hooks and routers, and
- log and audit all decisions.

The examples build on the core gateway concepts (`GatewayModel`, `GatewayGuardrail`, `GatewayConfig`) that you may already be using in your existing `model.py` configuration.



## 1. Guardrails in the Gateway Architecture

In the Practicus AI gateway, every request typically follows this high-level flow:

1. **Client request** → HTTP / OpenAI-compatible API
2. **Gateway guardrails & hooks** (input validation, transformation, enrichment)
3. **Model routing** (direct model call or virtual router)
4. **Gateway guardrails & hooks** (output validation, redaction, post-processing)
5. **Response back to the client**

By placing guardrails at both the **prompt** and **response** stages, the gateway can:

- prevent unsafe or policy-violating prompts from reaching any model,
- ensure that generated content is checked against organizational rules before it is returned,
- record decisions for audit and monitoring.

All of this is configured in Python in your `model.py` file, using the same patterns as the core gateway configuration.



## 2. Defining Prompt-Side Guardrails (Input Validation)

Prompt-side guardrails are responsible for inspecting and optionally transforming the incoming request **before** any model is called.

Typical use cases include:

- blocking clearly disallowed topics,
- enforcing ethical and legal usage rules,
- scrubbing or masking personal or confidential information,
- tagging requests with policy metadata for downstream analysis.

The gateway exposes this via the `GatewayGuardrail` class with a `mode` that runs before the model call (for example, `"pre_call"`).


```python
import practicuscore as prt

# A simple list of disallowed keywords for demonstration.
# In production, replace this with more advanced checks (regex, classifiers, etc.).
DISALLOWED_KEYWORDS: list[str] = [
    "do something bad",
    "credit card number",
]


async def block_disallowed_topics(data: dict, requester: dict | None = None, **kwargs) -> dict:
    """Input guardrail that blocks clearly disallowed topics at prompt time.

    - Inspects the full prompt transcript.
    - If a disallowed keyword is detected, rewrites the request so that:
      * nothing unsafe is sent to the model,
      * the client receives a clear, policy-compliant message.
    """
    messages: list[dict] = data.get("messages", [])
    full_text: str = "\n".join(m.get("content", "") for m in messages).lower()

    matched_keyword: str | None = None
    for keyword in DISALLOWED_KEYWORDS:
        if keyword in full_text:
            matched_keyword = keyword
            break

    # If there is no violation, forward the request unchanged.
    if matched_keyword is None:
        return data

    # Violation detected: do NOT send the original prompt to any model.
    # Instead, replace the prompt with a safe, explanatory message.
    safe_message: str = (
        "Your request cannot be processed because it violates the organization's safety and acceptable-use policies."
    )

    data["messages"] = [
        {
            "role": "assistant",
            "content": safe_message,
        }
    ]
    data["policy_decision"] = {
        "blocked": True,
        "reason": "disallowed_keyword",
        "keyword": matched_keyword,
    }

    return data


prompt_policy_guard = prt.GatewayGuardrail(
    name="prompt-policy-guard",
    mode="pre_call",  # Runs before the LLM is invoked
    guard=block_disallowed_topics,
    default_on=True,  # Enabled for all models by default
)

# In your gateway_conf you would register the guardrail:
#
# gateway_conf = prt.GatewayConfig(
#     models=[...],                    # your GatewayModel list
#     guardrails=[prompt_policy_guard],
# )
```

With this configuration:

- Any request that contains a disallowed keyword is intercepted **before** hitting an LLM.
- The user sees a clear, friendly explanation instead of a model-generated answer.
- The decision is recorded in `data["policy_decision"]`, which can be stored in the gateway's database logs for later review.



## 3. Output-Side Guardrails (Response Moderation)

Even when prompts look safe, generated content must still be checked before returning it to end users.

Output-side guardrails typically:

- detect sensitive or classified information in the response,
- prevent hate speech, self-harm instructions, or other harmful content from being exposed,
- enforce corporate communication and compliance rules,
- attach structured moderation metadata to each response.

The gateway uses the same `GatewayGuardrail` mechanism, but configured to run **after** the model call.


```python
import re

# Example patterns and flags for illustration only.
SENSITIVE_OUTPUT_PATTERNS: list[re.Pattern] = [
    re.compile(r"\bconfidential\b", re.IGNORECASE),
    re.compile(r"\btop secret\b", re.IGNORECASE),
]

BANNED_OUTPUT_FRAGMENTS: list[str] = [
    "how to do bad things",
    "hate-filled message",
]


def _extract_text_from_llm_response(data: dict) -> str:
    """Best-effort extraction of response text from an OpenAI-style response dict."""
    # Some gateways may store a flattened 'output_text'.
    if "output_text" in data and isinstance(data.get("output_text"), str):
        return data.get("output_text", "")

    # Fallback for standard chat.completions-style payloads.
    choices: list[dict] = data.get("choices", [])
    if choices:
        message: dict = choices[0].get("message", {})
        content: str = message.get("content", "") or ""
        return content

    return ""


def _write_text_back_to_response(data: dict, new_text: str) -> None:
    """Write a sanitized text back into the response structure."""
    if "output_text" in data:
        data["output_text"] = new_text
        return

    choices: list[dict] = data.get("choices", [])
    if not choices:
        data["choices"] = [
            {
                "message": {
                    "role": "assistant",
                    "content": new_text,
                }
            }
        ]
        return

    data["choices"][0].setdefault("message", {})
    data["choices"][0]["message"]["content"] = new_text


async def moderate_output(data: dict, requester: dict | None = None, **kwargs) -> dict:
    """Output guardrail that checks the generated text and applies moderation.

    - Detects simple sensitive markers and banned fragments.
    - If a violation is found, replaces the content with a safe message
      and records moderation metadata for audit.
    """
    generated_text: str = _extract_text_from_llm_response(data)
    lower_text: str = generated_text.lower()

    sensitive_match: bool = any(p.search(generated_text) for p in SENSITIVE_OUTPUT_PATTERNS)
    banned_match: bool = any(fragment in lower_text for fragment in BANNED_OUTPUT_FRAGMENTS)

    if not (sensitive_match or banned_match):
        # No violation detected, return the original response.
        return data

    safe_message: str = (
        "This answer was blocked by the gateway because it may contain sensitive or "
        "policy-violating information. Please rephrase your request or contact an administrator "
        "if you believe this is incorrect."
    )

    _write_text_back_to_response(data=data, new_text=safe_message)

    data["moderation"] = {
        "blocked": True,
        "sensitive_match": sensitive_match,
        "banned_match": banned_match,
    }

    return data


output_moderation_guard = prt.GatewayGuardrail(
    name="output-moderation-guard",
    mode="post_call",  # Runs after the LLM response is available
    guard=moderate_output,
    default_on=True,
)

# As with input guardrails, you register this in the gateway configuration:
#
# gateway_conf = prt.GatewayConfig(
#     models=[...],
#     guardrails=[
#         prompt_policy_guard,
#         output_moderation_guard,
#     ],
# )

```

This pattern ensures that:

- every model response is checked for sensitive or harmful content,
- blocked answers are replaced with a consistent, policy-aligned message,
- metadata under `data["moderation"]` can be stored for later audit or dashboards.



## 4. Composing Multiple Guardrails into a Reusable Policy

Real-world deployments rarely rely on a single rule. Instead, you typically combine several guardrails:

- **Prompt policy guard** for obvious violations in the input,
- **PII scrubber** to remove personal identifiers,
- **Output moderation guard** to filter unsafe generations,
- Optional, project-specific rules that individual teams can enable or disable.

All guardrails are defined once in `model.py` and then combined inside `GatewayConfig`.


```python
# Example PII scrubber.
async def scrub_basic_pii(data: dict, requester: dict | None = None, **kwargs) -> dict:
    """Naive PII scrubber that masks email addresses in messages."""
    messages: list[dict] = data.get("messages", [])
    for message in messages:
        content: str = message.get("content", "")
        # Very simple example; in production use a proper PII detection library.
        message["content"] = content.replace("@", " [at] ")
    data["messages"] = messages
    return data


pii_guard = prt.GatewayGuardrail(
    name="pii-scrubber",
    mode="pre_call",
    guard=scrub_basic_pii,
    default_on=False,  # available, but not forced for every model
)


# Combine everything in a single configuration object.
gateway_conf = prt.GatewayConfig(
    models=[
        # ... your GatewayModel instances, e.g. model_gpt_4o, model_hosted_vllm, routers, etc.
    ],
    guardrails=[
        prompt_policy_guard,
        output_moderation_guard,
        pii_guard,
    ],
    # database_url can be set here to store full request/response logs and policy metadata.
    # database_url="postgresql://user:password@db_host:5432/gateway",
)

```

Clients can explicitly opt in to non-default guardrails (like `"pii-scrubber"`) on a per-request basis using the standard OpenAI-compatible `extra_body` field:


```python
# Example client usage (Python, OpenAI-style client)
#
from openai import OpenAI

client = OpenAI(
    base_url="https://your-practicus-gateway.example.com/models",
    api_key="TOKEN_FROM_PRACTICUS",
)

response = client.chat.completions.create(
    model="practicus/gpt-4o",
    messages=[
        {"role": "user", "content": "Summarize this document..."},
    ],
    extra_body={
        "guardrails": [
            "pii-scrubber",  # opt-in
            # prompt-policy-guard and output-moderation-guard are default_on=True
        ]
    },
)

```

This gives platform administrators a way to define a **global baseline policy** (via `default_on=True` guardrails) and optional **project-level extensions** that teams can enable as needed.



## 5. Model-Level Hooks for Fine-Grained Control

In addition to gateway-wide guardrails, each `GatewayModel` can define its own hooks:

- `pre_guards` / `post_guards` – lists of async functions similar to guardrails, but tied to a single model,
- `pre_call` – invoked just before the LLM call for that model,
- `post_call_success` / `post_call_failure` – invoked after a successful or failed call (useful for logging and alerts).

This allows you to apply stricter rules to specific endpoints (for example, projects dealing with especially sensitive data) without affecting all models.


```python
# Example: a model for highly confidential workloads with extra checks.


async def high_sensitivity_pre_guard(data: dict, requester: dict | None = None, **kwargs) -> dict:
    """Extra checks for a high-sensitivity project.

    Here you can:
    - enforce stricter length limits,
    - enforce additional topic controls,
    - require that requester has a specific role.
    """
    if requester and "roles" in requester:
        roles: list[str] = requester.get("roles", [])
        if "high_sensitivity_project_user" not in roles:
            # Deny access by turning the request into a clear, safe message.
            data["messages"] = [
                {
                    "role": "assistant",
                    "content": "You are not authorized to use this model endpoint.",
                }
            ]
            data["policy_decision"] = {
                "blocked": True,
                "reason": "missing_role",
            }
            return data

    return data


async def log_high_sensitivity_usage(requester: dict | None = None, **kwargs) -> None:
    """Post-call hook that can send usage to a dedicated audit system."""
    user_id: str = requester.get("id", "anonymous") if requester else "anonymous"
    print(f"[AUDIT] High-sensitivity model used by user={user_id}")
    # Integrate here with your SIEM / logging platform if needed.


model_high_sensitivity = prt.GatewayModel(
    name="practicus/high-sensitivity-llm",
    model="openai/gpt-4o",  # or a Practicus-hosted model
    api_key_os_env="OPENAI_API_KEY",
    pre_guards=[
        block_disallowed_topics,  # reuse global building blocks
        high_sensitivity_pre_guard,
    ],
    post_guards=[
        moderate_output,  # reuse the output moderation guard
    ],
    post_call_success=log_high_sensitivity_usage,
)

```

By combining gateway-level guardrails with model-specific hooks, you can:

- enforce **organization-wide** safety and compliance rules,
- add **extra protections** for individual projects or departments,
- keep the implementation centralized and reusable.



## 6. Using Classification Models as Guardrails

For more advanced scenarios, organizations often prefer model-based moderation instead of simple keyword checks.

In this pattern:

1. A guard function extracts the user prompt or model output.
2. It calls a dedicated classification or moderation model (which can itself be exposed through the gateway).
3. Based on the resulting labels and scores, the guard function:
   - allows the request/response unchanged,
   - rewrites the content (for example, to a safer summary),
   - or blocks the interaction entirely.


```python
# Pseudo-code for a classification-based guardrail.
# Replace the commented section with a real client for your moderation model.


async def classify_and_enforce(data: dict, requester: dict | None = None, **kwargs) -> dict:
    """Guardrail that delegates the decision to a separate classification model.

    The model can return labels like:
    - ALLOWED
    - SENSITIVE
    - DISALLOWED

    and the gateway acts accordingly.
    """
    messages: list[dict] = data.get("messages", [])
    user_text: str = "\n".join(m.get("content", "") for m in messages)

    # In production, call your moderation endpoint here, for example:
    #
    # from openai import OpenAI
    #
    # moderation_client = OpenAI(
    #     base_url=os.environ.get("PRT_GATEWAY_BASE_URL"),
    #     api_key=os.environ.get("PRT_GATEWAY_API_KEY"),
    # )
    #
    # moderation_response = moderation_client.chat.completions.create(
    #     model="practicus/moderation-model",
    #     messages=[{"role": "user", "content": user_text}],
    # )
    #
    # label = moderation_response.choices[0].message.content.strip()
    #
    # For this example, we pretend we got a label from the model:
    label: str = "ALLOWED"

    if label == "ALLOWED":
        # let the request pass unchanged
        data.setdefault("moderation", {})
        data["moderation"]["label"] = label
        return data

    if label == "SENSITIVE":
        # allow, but annotate and possibly mask parts of the text
        data.setdefault("moderation", {})
        data["moderation"]["label"] = label
        data["moderation"]["note"] = "Handled as sensitive; please review downstream."
        return data

    # DISALLOWED or anything else: block / rewrite the request
    safe_message: str = (
        "Your request has been blocked by the organization's safety policies. "
        "Please contact an administrator if you believe this is an error."
    )
    data["messages"] = [
        {
            "role": "assistant",
            "content": safe_message,
        }
    ]
    data.setdefault("moderation", {})
    data["moderation"]["label"] = label
    data["moderation"]["blocked"] = True

    return data


classification_guard = prt.GatewayGuardrail(
    name="classification-based-guard",
    mode="pre_call",
    guard=classify_and_enforce,
    default_on=False,
)

```

This pattern lets you evolve your safety and ethics logic over time by simply improving the dedicated classification model, without changing application code that uses the gateway.



## 7. Logging, Auditing, and Explainability

Guardrails and hooks become much more powerful when combined with structured logging:

- Every decision (for example, blocked prompt, redacted output, detected PII) can be attached to the request/response payload under keys such as `policy_decision` or `moderation`.
- If `GatewayConfig.database_url` is configured, the gateway persists request and response metadata into a PostgreSQL database, including the extra fields your guardrails add.
- Additional hooks (such as `post_call_success`) can send summaries to SIEM systems, message queues, or monitoring tools.

A simple audit logging hook might look like this:


```python
async def audit_policy_decisions(data: dict, requester: dict | None = None, **kwargs) -> None:
    """Post-call hook that prints or forwards policy decisions for auditing.

    In a real deployment, replace the print() calls with structured logging or
    integration to your observability platform.
    """
    user_id: str = requester.get("id", "anonymous") if requester else "anonymous"
    policy_decision: dict | None = data.get("policy_decision")
    moderation_info: dict | None = data.get("moderation")

    print(f"[AUDIT] user={user_id} policy_decision={policy_decision} moderation={moderation_info}")


model_with_audit = prt.GatewayModel(
    name="practicus/audited-model",
    model="openai/gpt-4o",
    api_key_os_env="OPENAI_API_KEY",
    pre_guards=[block_disallowed_topics],
    post_guards=[moderate_output],
    post_call_success=audit_policy_decisions,
)

```

Together with the gateway's built-in database logging, this enables:

- traceability of who triggered which guardrails and when,
- investigations of edge cases or false positives,
- reporting on the overall health of LLM usage across the organization.



## 8. Using Machine-Learning–Based Guardrails

Static keyword lists are useful as a baseline, but they are hard to maintain at scale and easy to bypass.
In the Practicus AI Gateway, guardrails can also be powered by **machine learning models** and **LLMs**:

* **ML-based guardrails**: use traditional NLP models (e.g., PII detection, classification) to scan prompts and outputs.
* **LLM-based guardrails**: use an LLM specialized for safety or moderation (e.g., Llama Guard) to make context-aware decisions.

This lets policies evolve over time without changing application code: you can improve the underlying models, retrain them, or tune configuration while keeping the gateway integration stable.

<!-- #region -->
## 9. Machine-Learning–Based Guardrails (Example: Microsoft Presidio)

[Microsoft Presidio](https://github.com/microsoft/presidio) is an open-source toolkit for detecting and anonymizing PII.
You can integrate Presidio directly into a `GatewayGuardrail` to dynamically detect and redact sensitive data from prompts (or outputs) before they reach the model.

### 9.1. Installing and Configuring Presidio

Presidio typically consists of two main components:

* `AnalyzerEngine` – detects entities such as names, email addresses, phone numbers.
* `AnonymizerEngine` – redacts or masks the detected entities.

Install (example):

```bash
pip install presidio-analyzer presidio-anonymizer
```

### 9.2. Using Presidio as a Prompt Guardrail

Below is an example of a **pre-call** guardrail that:

1. Extracts the user messages from the request.
2. Uses Presidio to detect PII.
3. Anonymizes the PII before passing the request to the LLM.
4. Adds metadata about what was redacted for auditing.

<!-- #endregion -->

```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
import practicuscore as prt

# Initialize engines once at module import time
presidio_analyzer: AnalyzerEngine = AnalyzerEngine()
presidio_anonymizer: AnonymizerEngine = AnonymizerEngine()

PII_ENTITIES: list[str] = [
    "PERSON",
    "PHONE_NUMBER",
    "EMAIL_ADDRESS",
    "CREDIT_CARD",
]


def _anonymize_text_with_presidio(text: str) -> tuple[str, list[dict]]:
    """Run Presidio analyzer + anonymizer on a single string."""
    results = presidio_analyzer.analyze(
        text=text,
        entities=PII_ENTITIES,
        language="en",
    )

    anonymized_result = presidio_anonymizer.anonymize(
        text=text,
        analyzer_results=results,
        # Use a simple anonymization policy; can be customized per entity
        anonymizers={
            "DEFAULT": {
                "type": "replace",
                "new_value": "[PII]",
            }
        },
    )

    anonymized_text: str = anonymized_result.text
    findings: list[dict] = [
        {
            "entity_type": r.entity_type,
            "start": r.start,
            "end": r.end,
            "score": r.score,
        }
        for r in results
    ]
    return anonymized_text, findings


async def presidio_pii_guard(
    data: dict,
    requester: dict | None = None,
    **kwargs,
) -> dict:
    """
    Guardrail that uses Microsoft Presidio to detect and redact PII
    in the user's prompt before sending it to any model.

    - All user messages are scanned.
    - Detected PII tokens are replaced with [PII].
    - A summary of findings is attached under data["pii_scan"].
    """
    messages: list[dict] = data.get("messages", [])
    all_findings: list[dict] = []

    for message in messages:
        if message.get("role") != "user":
            continue

        original_content: str = message.get("content", "") or ""
        if not original_content.strip():
            continue

        anonymized_text, findings = _anonymize_text_with_presidio(original_content)

        message["content"] = anonymized_text
        if findings:
            all_findings.extend(
                {
                    "role": message.get("role", "user"),
                    "entity_type": f["entity_type"],
                    "score": f["score"],
                }
                for f in findings
            )

    if all_findings:
        data.setdefault("pii_scan", {})
        data["pii_scan"]["engine"] = "microsoft_presidio"
        data["pii_scan"]["findings"] = all_findings

    return data


presidio_pii_guardrail = prt.GatewayGuardrail(
    name="ml-pii-guard",
    mode="pre_call",  # runs before the LLM call
    guard=presidio_pii_guard,
    default_on=False,  # opt-in or enable per-project
)

# Example: add to your gateway configuration
# gateway_conf = prt.GatewayConfig(
#     models=[...],
#     guardrails=[
#         prompt_policy_guard,
#         output_moderation_guard,
#         presidio_pii_guardrail,
#     ],
# )
```

**Key points:**

* The **policy logic** is encoded in Presidio configuration and models, not in hard-coded regexes.
* Updating entity types, thresholds, or recognizers immediately changes protection behavior.
* You can apply the same pattern to **output-side** guards (using `mode="post_call"`) if you want to scan and redact responses.



## 10. LLM-Based Guardrails (Example: Llama Guard)

Instead of rule-based or classical ML, you can also use **LLMs** as guardrails.
A specialized safety model like **Llama Guard** can evaluate prompts and responses using rich context:

* Understanding nuanced intent (sarcasm, indirect instructions).
* Considering multi-turn conversation history.
* Applying complex policy descriptions written in natural language.

In this pattern, the gateway:

1. Prepares a concise representation of the conversation.
2. Sends it to a safety LLM (e.g., a gateway-exposed model `practicus/llamaguard`).
3. Interprets the LLM’s verdict (e.g., `ALLOWED` / `BLOCKED` + reasons).
4. Decides whether to forward the request to the target LLM or to block/modify it.

### 10.1. Calling a Llama Guard Model from a Guardrail

Below is an example of a **pre-call** guardrail that calls a Llama Guard endpoint exposed through the same gateway. The Llama Guard model is treated like any other `GatewayModel` (e.g., `practicus/llamaguard`).

```python
import os
from openai import OpenAI
import practicuscore as prt

# Client configured to talk to the Practicus gateway itself,
# where a `practicus/llamaguard` model is deployed.
llamaguard_client = OpenAI(
    base_url=os.environ.get("PRT_GATEWAY_BASE_URL"),  # e.g. https://gateway.example.com/models
    api_key=os.environ.get("PRT_GATEWAY_API_KEY"),  # token issued by Practicus AI
)

LLAMAGUARD_SYSTEM_PROMPT: str = """
You are a safety classifier for an enterprise AI assistant.

Given a user request (and optional assistant messages), decide whether the
conversation is SAFE or UNSAFE according to the organization's policies.

Respond ONLY with a single JSON object on one line:

{
  "label": "SAFE" | "UNSAFE",
  "categories": [ ... ],      // list of relevant policy categories, can be empty
  "explanation": "..."        // short explanation
}
"""


def _conversation_to_text(messages: list[dict]) -> str:
    """Flatten messages into a simple text snippet for the safety model."""
    parts: list[str] = []
    for m in messages:
        role: str = m.get("role", "user")
        content: str = m.get("content", "") or ""
        parts.append(f"{role.upper()}: {content}")
    return "\n".join(parts)


async def llamaguard_prompt_filter(
    data: dict,
    requester: dict | None = None,
    **kwargs,
) -> dict:
    """
    Guardrail that uses a Llama Guard model to classify the safety of the prompt.

    - Sends the conversation so far to `practicus/llamaguard`.
    - If label == SAFE, the request is forwarded unchanged.
    - If label == UNSAFE, the request is blocked and replaced with a safe message.
    """
    messages: list[dict] = data.get("messages", [])
    if not messages:
        return data

    text_for_guard: str = _conversation_to_text(messages)

    # Call the Llama Guard endpoint (OpenAI-compatible)
    safety_response = llamaguard_client.chat.completions.create(
        model="practicus/llamaguard",
        messages=[
            {"role": "system", "content": LLAMAGUARD_SYSTEM_PROMPT},
            {"role": "user", "content": text_for_guard},
        ],
        temperature=0.0,
    )

    safety_raw: str = safety_response.choices[0].message.content.strip()
    # For simplicity assume the response is valid JSON; in production, wrap in try/except.
    import json

    safety_json: dict = json.loads(safety_raw)
    label: str = safety_json.get("label", "SAFE")
    categories: list[str] = safety_json.get("categories", [])
    explanation: str = safety_json.get("explanation", "")

    # Attach the moderation info to the request for auditing
    data.setdefault("llm_guard", {})
    data["llm_guard"]["label"] = label
    data["llm_guard"]["categories"] = categories
    data["llm_guard"]["explanation"] = explanation

    if label.upper() == "SAFE":
        # Forward the request unchanged
        return data

    # UNSAFE: block or rewrite the interaction
    safe_message: str = (
        "Your request cannot be processed because it violates the safety and usage "
        "policies defined for this assistant. If you believe this is a mistake, "
        "please contact your system administrator."
    )

    data["messages"] = [
        {
            "role": "assistant",
            "content": safe_message,
        }
    ]
    data["llm_guard"]["blocked"] = True

    return data


llamaguard_guardrail = prt.GatewayGuardrail(
    name="llm-llamaguard-prompt-guard",
    mode="pre_call",  # classify before calling the main model
    guard=llamaguard_prompt_filter,
    default_on=False,  # can be enabled for specific projects or endpoints
)

# Example: adding to the configuration
# gateway_conf = prt.GatewayConfig(
#     models=[..., model_high_sensitivity, ...],
#     guardrails=[
#         prompt_policy_guard,
#         output_moderation_guard,
#         presidio_pii_guardrail,
#         llamaguard_guardrail,
#     ],
# )

```

### 10.2. Why Use LLMs as Guardrails?

Compared to static rules, LLM-based guardrails:

* **Understand context**: multi-turn, subtle phrasing, indirect hints.
* **Adapt via prompts**: changing the system prompt adjusts policy behavior without code changes.
* **Handle complex categories**: legal, ethical, domain-specific rules written in natural language.

You can also:

* run Llama Guard (or similar) on **outputs** by using `mode="post_call"`,
* chain multiple guard models (e.g., first PII/Presidio, then safety/LLM),
* or use one LLM guard to implement a “second opinion” for specific high-risk models.



### 10.3. Dynamic Guardrails in Practice

By combining ML- and LLM-based guardrails:

* **Policies become dynamic**: updating the Presidio configuration, retraining a classifier, or revising the Llama Guard prompt changes behavior without touching application code.
* **Different projects can opt into different profiles**:

  * strict PII + safety for healthcare or finance workloads,
  * lighter checks for internal experimentation,
  * custom categories for specific departments.
* **Auditability is built in**: both Presidio findings (`data["pii_scan"]`) and Llama Guard decisions (`data["llm_guard"]`) can be logged, queried, and visualized in your existing observability stack.

This turns the gateway into a **policy engine** that can evolve with organizational requirements, rather than a static set of hard-coded filters.



## 11. Summary

Using the patterns in this example, you can configure the Practicus AI gateway to:

- inspect and regulate prompts before they reach any LLM,
- moderate and, if needed, block or rewrite model outputs,
- combine reusable guardrails into organization-wide and project-specific policies,
- integrate advanced classification-based moderation where required,
- log and audit all decisions for transparency and compliance.
- Use ML based guardrails instead of static rules.

All of this is defined in Python in your `model.py`, leveraging `GatewayModel`, `GatewayGuardrail`, `GatewayConfig`, and the hook system that the gateway already uses for routing and logging. This keeps safety and policy enforcement close to the models, while remaining easy to maintain and extend as requirements evolve.



---

**Previous**: [Model Gateway](model-gateway.md) | **Next**: [Custom > Models > Build](../custom/models/build.md)
