---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.3
  kernelspec:
    display_name: practicus_genai
    language: python
    name: python3
---

```python
# Parameters: Replace with your actual deployment key and app prefix
# These identify where the app should be deployed within your Practicus AI environment.
app_deployment_key = None
app_prefix = "apps"
```

```python
assert app_deployment_key, "Please select a deployment key"
```

```python
import practicuscore as prt

# Analyze the current directory for Practicus AI App components (APIs, MQ consumers, UI, etc.)
# This should output the list of detected API endpoints.
prt.apps.analyze()
```

```python
# --- Deployment ---
app_name = "agentic-ai-test-retention"
visible_name = "Agentic AI Test retention"
description = "Test Application for Agentic AI Example."
icon = "fa-robot"

print(f"Deploying app '{app_name}'...")

app_url, api_url = prt.apps.deploy(
    deployment_setting_key=app_deployment_key,
    prefix=app_prefix,
    app_name=app_name,
    app_dir=None,  # Uses current directory
    visible_name=visible_name,
    description=description,
    icon=icon,
)

print("App deployed successfully!")
print(f"  API Base URL: {api_url}")

# The OpenAPI (Swagger) documentation (Swagger/ReDoc) is usually available at /docs or /redoc off the API base URL
print(f"  OpenAPI (Swagger) Docs (ReDoc): {api_url}redoc/")

# Store the api_url for later use when creating tools
assert api_url, "Deployment failed to return an API URL."
```

```python
tool_endpoint_paths = [
    "aggregate-retention-insight-report/",
    "analyze-complaint-topics/",
    "analyze-sentiment-trends/",
    "detect-negative-sentiment-clusters/",
    "generate-customer-summary/",
    "generate-retention-plan/",
    "generate-retention-risk-scores/",
    "load-customer-interaction-data/",
    "summarize-customer-retention-case/",
    "visualize-customer-journey-map/",
]


# Construct full URLs
tool_endpoint_urls = [api_url + path for path in tool_endpoint_paths]

print("Will attempt to create tools for the following API endpoints:")
for url in tool_endpoint_urls:
    print(f" - {url}")

# Tip: If you pass partial API URLs e.g. 'apps/agentic-ai-test/api/v1/generate-receipt/'
#  The base URL e.g. 'https://practicus.my-company.com/' will be added to the final URL
#  using your current Practicus AI region.
```

```python
import os
from langchain_openai import ChatOpenAI  # Or your preferred ChatModel
from langgraph.prebuilt import create_react_agent
from langchain_practicus import APITool

# Ensure practicuscore is imported for enums
import practicuscore as prt


def validate_api_spec(api_tool: APITool, strict=False) -> bool:
    """Checks the APISpec of a fetched tool against our rules."""

    # APITool fetches the spec from OpenAPI (Swagger) during initialization
    spec = api_tool.spec

    if not spec:
        # API definition in the source file might be missing the 'spec' object
        warning_msg = f"API '{api_tool.url}' does not have APISpec metadata defined in its OpenAPI spec."
        if strict:
            raise ValueError(f"{warning_msg} Validation is strict.")
        else:
            prt.logger.warning(f"{warning_msg} Allowing since validation is not strict.")
            return True  # Allow if not strict

    # --- Apply Rules based on fetched spec ---

    # Rule 1: Check Risk Profile
    if spec.risk_profile and spec.risk_profile == prt.APIRiskProfile.High:
        err = f"API '{api_tool.url}' has a risk profile defined as '{spec.risk_profile}'."
        if strict:
            err += " Stopping flow since validation is strict."
            raise ValueError(err)
        else:
            # Even if not strict, we might choose to block High risk tools
            prt.logger.warning(f"{err} Blocking High Risk API even though validation is not strict.")
            return False  # Block high risk

    # Rule 2: Check Human Gating for non-read-only APIs
    # (Example: Enforce human gating for safety on modifying APIs)
    if not spec.read_only and not spec.human_gated:
        err = f"API '{api_tool.url}' modifies data (read_only=False) but is not marked as human_gated."
        if strict:
            err += " Stopping flow since validation is strict."
            raise ValueError(err)
        else:
            prt.logger.warning(f"{err} Allowing non-gated modifying API since validation is not strict.")
            # In this non-strict case, we allow it, but a stricter policy might return False here.
            return True

    # Add more complex rules here if needed...
    # E.g., check custom_attributes, scope, etc.

    # If no rules were violated (or violations were allowed because not strict)
    prt.logger.info(f"API '{api_tool.url}' passed validation (strict={strict}). Spec: {spec}")
    return True


# --- Create Tools (optionally applying validation) ---
def get_tools(endpoint_urls: list[str], validate=True):
    _tools = []
    strict_validation = False  # Set to True to enforce stricter rules
    additional_instructions = "Add Yo! after all of your final responses."  # Example instruction

    print(f"\nCreating and validating tools (strict={strict_validation})...")
    for tool_endpoint_url in endpoint_urls:
        print(f"\nProcessing tool for API: {tool_endpoint_url}")
        try:
            api_tool = APITool(
                url=tool_endpoint_url,
                additional_instructions=additional_instructions,
                # token=..., # Uses current user credentials by default, set to override
                # include_resp_schema=True # Response schema (if exists) is not included by default
            )

            # Explain the tool (optional, useful for debugging)
            # api_tool.explain(print_on_screen=True)

            # Validate based on fetched APISpec
            if not validate or validate_api_spec(api_tool=api_tool, strict=strict_validation):
                print(
                    f"--> Adding tool: {api_tool.name} ({api_tool.url}) {'' if validate else ' - skipping validation'}"
                )
                _tools.append(api_tool)
            else:
                print(f"--> Skipping tool {api_tool.name} due to validation rules.")
        except Exception as e:
            # Catch potential errors during APITool creation (e.g., API not found, spec parsing error)
            print(f"ERROR: Failed to create or validate tool for {tool_endpoint_url}: {e}")
            if strict_validation:
                raise  # Re-raise if strict
            else:
                print("--> Skipping tool due to error (not strict).")

    return _tools


tools = get_tools(tool_endpoint_urls)
print(f"\nAgent will have access to {len(tools)} tools: {[t.name for t in tools]}")
```

```python
# For this excercise we will skip validating APIs

tools = get_tools(tool_endpoint_urls, validate=False)
print(f"\nAgent will have access to {len(tools)} tools: {[t.name for t in tools]}")
```

```python
# View tool explanation

for tool in tools:
    tool.explain()
```

```python
openaikey, age = prt.vault.get_secret("openaikey")
os.environ["OPENAI_API_KEY"] = openaikey

assert os.environ["OPENAI_API_KEY"], "OpenAI key is not defined"
```

```python
# --- Agent Initialization ---
llm = ChatOpenAI(model="gpt-4o", temperature=0)
# Create a ReAct agent using LangGraph
graph = create_react_agent(llm, tools=tools)
print("Agent initialized.")


# Helper function to print the agent's stream output nicely
def pretty_print_stream_chunk(chunk):
    print("--- Agent Step ---")
    for node, updates in chunk.items():
        print(f"Node: {node}")
        if isinstance(updates, dict) and "messages" in updates:
            # Print the latest message added by the node
            latest_message = updates["messages"][-1]
            latest_message.pretty_print()
        else:
            # Print other kinds of updates
            print(f"  Update: {updates}")
    print("--------------------\n")
```

```python
def pretty_print_stream_chunk2(chunk):
    print("--- Agent Step ---")
    for node, updates in chunk.items():
        print(f"Node: {node}")
        if isinstance(updates, dict) and "messages" in updates:
            latest_message = updates["messages"][-1]
            latest_message.pretty_print()
        else:
            print(f"  Update: {updates}")
            if isinstance(updates, Exception):
                print("  ⚠️ Exception Detected in Agent Execution!")
    print("--------------------\n")

```

```python
query = """
Identify clusters of customers who are expressing negative sentiment in their recent feedback, broken down by date and channel. I want to detect any spikes or trends that might indicate dissatisfaction periods.
"""


inputs = {"messages": [("user", query)]}

if graph:
    print(f"\nInvoking agent with query: '{query}'")
    print("Streaming agent execution steps:\n")

    # Configuration for the stream, e.g., setting user/thread IDs
    # config = {"configurable": {"user_id": "doc-user-1", "thread_id": "doc-thread-1"}}
    config = {}
    # Use astream to get intermediate steps
    async for chunk in graph.astream(inputs, config=config):
        pretty_print_stream_chunk2(chunk)

    print("\nAgent execution finished.")

    # Optional: Get the final state if needed
    # final_state = await graph.ainvoke(inputs, config=config)
    # print("\nFinal Agent State:", final_state)

else:
    print("\nAgent execution skipped because the agent graph was not initialized.")
```

```python
# Cleanup
prt.apps.delete(prefix=app_prefix, app_name=app_name)
```

API TEST

```python
from apis.analyze_sales_trends import AnalyzeSalesTrendsRequest, AnalyzeSalesTrendsResponse, SalesRecord
from datetime import datetime
import practicuscore as prt

sales_data = [
    SalesRecord(date=datetime(2025, 1, 1), product="Laptop", region="Asia", units_sold=100, revenue=100000.0),
    SalesRecord(date=datetime(2025, 1, 2), product="Laptop", region="Asia", units_sold=120, revenue=120000.0),
    SalesRecord(date=datetime(2025, 1, 3), product="Tablet", region="Europe", units_sold=80, revenue=32000.0),
]

payload = AnalyzeSalesTrendsRequest(
    sales_data=sales_data, start_date=datetime(2025, 1, 1), end_date=datetime(2025, 1, 3)
)

response: AnalyzeSalesTrendsResponse = prt.apps.test_api("/analyze-sales-trends", payload)

print(response)

```

```python
from apis.sentiment_test_slogan import SentimentTestSloganRequest, SentimentTestSloganResponse
from pydantic import BaseModel
import practicuscore as prt

# Prepare payload
slogans = [
    "Power Up Your Productivity!",
    "Nothing beats the classics.",
    "Innovation in Every Click.",
    "Your Tech, Your Edge.",
    "Be Bold. Be Better.",
]
payload = SentimentTestSloganRequest(slogans=slogans)

# Type check (optional)
print(issubclass(type(payload), BaseModel))  # Should print True

# Local test via Practicus
response: SentimentTestSloganResponse = prt.apps.test_api("/sentiment-test-slogan", payload)

# Output the results
for result in response.results:
    print(f"Slogan: {result.slogan}")
    print(f"Sentiment: {result.sentiment}")
    print(f"Comment: {result.comment}")
    print("-----")

```

```python
from apis.top_products_insight import TopProductsInsightRequest, TopProductsInsightResponse, SalesRecord
from pydantic import BaseModel
from datetime import datetime
import practicuscore as prt

# Örnek satış verisi
sales_data = [
    SalesRecord(date=datetime(2025, 1, 1), product="Laptop", region="Asia", units_sold=120, revenue=120000.0),
    SalesRecord(date=datetime(2025, 1, 2), product="Laptop", region="Asia", units_sold=100, revenue=100000.0),
    SalesRecord(date=datetime(2025, 1, 3), product="Tablet", region="Europe", units_sold=80, revenue=32000.0),
    SalesRecord(date=datetime(2025, 1, 4), product="Tablet", region="Europe", units_sold=70, revenue=28000.0),
    SalesRecord(date=datetime(2025, 1, 5), product="Monitor", region="North America", units_sold=95, revenue=47500.0),
]

# Test payload
payload = TopProductsInsightRequest(sales_data=sales_data, top_n=3)

# API test
try:
    response: TopProductsInsightResponse = prt.apps.test_api("/top-products-insight", payload)

    # Sonuçları yazdır
    for product in response.products:
        print(f"Product: {product.product}")
        print(f"Total Units Sold: {product.total_units_sold}")
        print(f"Top Region: {product.top_region}")
        print(f"Insight: {product.insight}")
        print("-----")

except Exception as e:
    prt.logger.error(f"[test-top-products-insight] Exception: {e}")
    raise

```

```python
from practicuscore import apps
from apis.predict_growth_opportunities import PredictGrowthOpportunitiesRequest

payload = PredictGrowthOpportunitiesRequest(
    top_products=[{"product": "Tablet", "total_units_sold": 305, "top_region": "Asia"}],
    regional_drops=[{"region": "Europe", "product": "Tablet", "drop_percentage": 100.0}],
    trend_summary={"trend_direction": "increasing", "peak_day": "2025-01-10"},
)

response = apps.test_api("/predict-growth-opportunities", payload)
print(response)

```

```python
from apis.predict_growth_opportunities import run, PredictGrowthOpportunitiesRequest

payload = PredictGrowthOpportunitiesRequest(
    top_products=[{"product": "Tablet", "total_units_sold": 305, "top_region": "Asia"}],
    regional_drops=[{"region": "Europe", "product": "Tablet", "drop_percentage": 100.0}],
    trend_summary={"trend_direction": "increasing", "peak_day": "2025-01-10"},
)

await run(payload)

```

```python

```


## Supplementary Files

### apis/aggregate_retention_insight_report.py
```python
# apis/aggregate_retention_insight_report.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List, Dict


class CustomerRetentionCase(BaseModel):
    customer_id: str
    """ID of the customer evaluated for retention."""

    churn_risk: str
    """Detected churn risk level: low, medium, or high."""

    complaint_topic: str
    """Most prominent complaint theme, extracted via feedback analysis."""

    retention_action: str
    """Suggested key retention action from the plan."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C088",
                    "churn_risk": "high",
                    "complaint_topic": "billing errors",
                    "retention_action": "offer billing correction and compensation"
                }
            ]
        }
    }


class AggregateRetentionInsightRequest(BaseModel):
    retention_cases: List[CustomerRetentionCase]
    """Retention-level insights for each customer including root cause and remedy."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "retention_cases": [
                        {
                            "customer_id": "C088",
                            "churn_risk": "high",
                            "complaint_topic": "billing errors",
                            "retention_action": "offer billing correction and compensation"
                        }
                    ]
                }
            ]
        }
    }


class InsightSummary(BaseModel):
    key_findings: List[str]
    """Executive summary of key findings from churn analysis."""

    dominant_issues: Dict[str, int]
    """Complaint topic frequency distribution."""

    churn_risk_distribution: Dict[str, int]
    """Count of customers by churn risk level."""

    strategic_recommendation: str
    """Final LLM-generated strategic recommendation summary."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "key_findings": [
                        "Most churn risk is observed in mid-tier accounts",
                        "Support-related issues dominate complaint patterns"
                    ],
                    "dominant_issues": {
                        "support delays": 12,
                        "billing errors": 9,
                        "missing features": 5
                    },
                    "churn_risk_distribution": {
                        "high": 14,
                        "medium": 22,
                        "low": 64
                    },
                    "strategic_recommendation": "Invest in proactive support, improve billing clarity, and introduce churn detection triggers for mid-risk customers."
                }
            ]
        }
    }


class AggregateRetentionInsightResponse(BaseModel):
    summary: InsightSummary
    """Top-level synthesized insight report for decision makers."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "summary": {
                        "key_findings": [
                            "Most churn risk is observed in mid-tier accounts",
                            "Support-related issues dominate complaint patterns"
                        ],
                        "dominant_issues": {
                            "support delays": 12,
                            "billing errors": 9,
                            "missing features": 5
                        },
                        "churn_risk_distribution": {
                            "high": 14,
                            "medium": 22,
                            "low": 64
                        },
                        "strategic_recommendation": "Invest in proactive support, improve billing clarity, and introduce churn detection triggers for mid-risk customers."
                    }
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    interactive=True,
    risk_profile=prt.APIRiskProfile.Low
)


@prt.api("/aggregate-retention-insight-report", spec=api_spec)
async def run(payload: AggregateRetentionInsightRequest, **kwargs) -> AggregateRetentionInsightResponse:
    """
    Aggregates individual customer churn analyses into a strategic retention report.
    """
    risk_counts = {"low": 0, "medium": 0, "high": 0}
    issue_counts = {}

    for case in payload.retention_cases:
        risk_counts[case.churn_risk] += 1
        issue_counts[case.complaint_topic] = issue_counts.get(case.complaint_topic, 0) + 1

    key_findings = [
        f"{risk_counts['high']} customers are at high churn risk.",
        f"Top issues include: {', '.join(sorted(issue_counts, key=issue_counts.get, reverse=True)[:3])}."
    ]

    recommendation = (
        "Focus on proactive outreach for high-risk clients, resolve the top 2 complaint topics,"
        " and monitor medium-risk customers with automated engagement campaigns."
    )

    return AggregateRetentionInsightResponse(
        summary=InsightSummary(
            key_findings=key_findings,
            dominant_issues=issue_counts,
            churn_risk_distribution=risk_counts,
            strategic_recommendation=recommendation
        )
    )

```

### apis/analyze_complaint_topics.py
```python
# apis/analyze_complaint_topics.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List, Dict
from collections import Counter
import re


class Complaint(BaseModel):
    customer_id: str
    """Customer's unique identifier."""

    complaint_text: str
    """Free-form text describing a customer's complaint."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {"customer_id": "C001", "complaint_text": "Service was too slow and no one responded to my emails."},
                {"customer_id": "C002", "complaint_text": "Billing is incorrect for the last two months!"}
            ]
        }
    }


class ComplaintTopic(BaseModel):
    topic: str
    """Identified complaint topic keyword or phrase."""

    count: int
    """Number of times the topic was detected."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [{"topic": "billing", "count": 5}, {"topic": "support", "count": 3}]
        }
    }


class AnalyzeComplaintTopicsRequest(BaseModel):
    complaints: List[Complaint]
    """List of raw customer complaints."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "complaints": [
                        {"customer_id": "C001", "complaint_text": "Your mobile app keeps crashing."},
                        {"customer_id": "C002", "complaint_text": "The delivery was delayed twice."}
                    ]
                }
            ]
        }
    }


class AnalyzeComplaintTopicsResponse(BaseModel):
    topics: List[ComplaintTopic]
    """Most frequent complaint topics extracted from the text corpus."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": {
                "topics": [
                    {"topic": "app crash", "count": 4},
                    {"topic": "delivery delay", "count": 3}
                ]
            }
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low
)


@prt.api("/analyze-complaint-topics", spec=api_spec)
async def run(payload: AnalyzeComplaintTopicsRequest, **kwargs) -> AnalyzeComplaintTopicsResponse:
    """
    Extracts the most common complaint topics from free-text customer complaints.
    """

    topic_keywords = ["billing", "delivery", "support", "login", "app", "refund", "delay", "payment", "email", "cancel"]
    topic_counter = Counter()

    for complaint in payload.complaints:
        text = complaint.complaint_text.lower()
        for keyword in topic_keywords:
            if re.search(rf"\b{re.escape(keyword)}\b", text):
                topic_counter[keyword] += 1

    topics = [ComplaintTopic(topic=k, count=v) for k, v in topic_counter.most_common()]

    return AnalyzeComplaintTopicsResponse(topics=topics)

```

### apis/analyze_sentiment_trends.py
```python
# apis/analyze_sentiment_trends.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List, Dict
from collections import defaultdict
import pandas as pd


class CustomerInteraction(BaseModel):
    customer_id: str
    """Unique identifier for the customer."""

    interaction_date: str
    """Date of the customer interaction."""

    channel: str
    """Communication channel (e.g. Email, Phone, Chat)."""

    sentiment_score: float
    """Sentiment score of the interaction (-1 to 1)."""

    issue_type: str
    """Category of the customer's issue or concern."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C12345",
                    "interaction_date": "2024-05-10",
                    "channel": "Email",
                    "sentiment_score": -0.45,
                    "issue_type": "Billing"
                }
            ]
        },
    }


class AnalyzeSentimentTrendsRequest(BaseModel):
    interactions: List[CustomerInteraction]
    """List of customer interaction records."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "interactions": [
                        {
                            "customer_id": "C12345",
                            "interaction_date": "2024-05-10",
                            "channel": "Email",
                            "sentiment_score": -0.45,
                            "issue_type": "Billing"
                        }
                    ]
                }
            ]
        },
    }


class SentimentTrend(BaseModel):
    period: str
    """Time period label (e.g., '2024-05')."""

    average_sentiment: float
    """Average sentiment score for that period."""


class AnalyzeSentimentTrendsResponse(BaseModel):
    trends: List[SentimentTrend]
    """List of sentiment trend entries across time."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "trends": [
                        {"period": "2024-05", "average_sentiment": -0.21}
                    ]
                }
            ]
        },
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low,
)


@prt.api("/analyze-sentiment-trends", spec=api_spec)
async def run(payload: AnalyzeSentimentTrendsRequest, **kwargs) -> AnalyzeSentimentTrendsResponse:
    """
    Analyze sentiment trends over time by grouping customer interactions monthly
    and computing the average sentiment score per period.
    """
    df = pd.DataFrame([i.model_dump() for i in payload.interactions])
    df["interaction_date"] = pd.to_datetime(df["interaction_date"])
    df["period"] = df["interaction_date"].dt.to_period("M").astype(str)

    trend_df = df.groupby("period")["sentiment_score"].mean().reset_index()
    trend_df.columns = ["period", "average_sentiment"]

    trends = [
        SentimentTrend(period=row["period"], average_sentiment=row["average_sentiment"])
        for _, row in trend_df.iterrows()
    ]

    return AnalyzeSentimentTrendsResponse(trends=trends)

```

### apis/detect_negative_sentiment_clusters.py
```python
# apis/detect_negative_sentiment_clusters.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd


class CustomerInteraction(BaseModel):
    customer_id: str
    """Unique identifier for the customer."""

    interaction_date: str
    """Date of the customer interaction."""

    channel: str
    """Communication channel used (e.g., Phone, Email, Chat)."""

    sentiment_score: Optional[float] = None
    """Sentiment score of the message (-1 = negative, 1 = positive)."""

    issue_type: str
    """Type or category of the customer issue (e.g., 'Delivery', 'Billing')."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C12345",
                    "interaction_date": "2024-05-10",
                    "channel": "Chat",
                    "sentiment_score": -0.9,
                    "issue_type": "Technical"
                }
            ]
        },
    }


class DetectNegativeClustersRequest(BaseModel):
    interactions: List[CustomerInteraction]
    """List of past customer interaction records."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "interactions": [
                        {
                            "customer_id": "C12345",
                            "interaction_date": "2024-05-10",
                            "channel": "Chat",
                            "sentiment_score": -0.9,
                            "issue_type": "Technical"
                        }
                    ]
                }
            ]
        },
    }


class SentimentCluster(BaseModel):
    time_window: str
    """Time window (e.g., day or week) in which a negative sentiment spike occurred."""

    channel: str
    """The communication channel where the spike was observed."""

    avg_sentiment: float
    """Average sentiment score in this cluster."""

    interaction_count: int
    """Number of negative interactions detected."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "time_window": "2024-05-10",
                    "channel": "Chat",
                    "avg_sentiment": -0.85,
                    "interaction_count": 17
                }
            ]
        },
    }


class DetectNegativeClustersResponse(BaseModel):
    clusters: List[SentimentCluster]
    """List of negative sentiment clusters grouped by time and channel."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "clusters": [
                        {
                            "time_window": "2024-05-10",
                            "channel": "Chat",
                            "avg_sentiment": -0.85,
                            "interaction_count": 17
                        }
                    ]
                }
            ]
        },
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
)


@prt.api("/detect-negative-sentiment-clusters", spec=api_spec)
async def run(payload: DetectNegativeClustersRequest, **kwargs) -> DetectNegativeClustersResponse:
    """
    Detects clusters of interactions with highly negative sentiment
    by grouping by day and communication channel.
    This helps identify periods of customer dissatisfaction spikes.
    """
    df = pd.DataFrame([i.model_dump() for i in payload.interactions])

    df["interaction_date"] = pd.to_datetime(df["interaction_date"])
    df["date"] = df["interaction_date"].dt.date

    # Filter out rows with null sentiment_score
    df = df[df["sentiment_score"].notnull()]

    # Filter for strongly negative interactions
    negative_df = df[df["sentiment_score"] < -0.6]

    grouped = negative_df.groupby(["date", "channel"]).agg(
        avg_sentiment=("sentiment_score", "mean"),
        interaction_count=("sentiment_score", "count")
    ).reset_index()

    clusters = [
        SentimentCluster(
            time_window=str(row["date"]),
            channel=row["channel"],
            avg_sentiment=round(row["avg_sentiment"], 2),
            interaction_count=row["interaction_count"]
        )
        for _, row in grouped.iterrows()
    ]

    return DetectNegativeClustersResponse(clusters=clusters)

```

### apis/generate_customer_summary.py
```python
# apis/generate_customer_summary.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List, Optional


class CustomerSignal(BaseModel):
    customer_id: str
    """Unique identifier for the customer."""

    loyalty_score: Optional[float]
    """Predicted loyalty score based on engagement and sentiment."""

    churn_risk: Optional[str]
    """Level of churn risk: low, medium, or high."""

    dominant_complaint_topic: Optional[str]
    """Most frequently detected complaint topic, if any."""

    feedback_sentiment: Optional[str]
    """Overall sentiment from feedback data (e.g., positive, neutral, negative)."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C021",
                    "loyalty_score": 0.82,
                    "churn_risk": "low",
                    "dominant_complaint_topic": "billing",
                    "feedback_sentiment": "positive"
                }
            ]
        }
    }


class GenerateCustomerSummaryRequest(BaseModel):
    signals: List[CustomerSignal]
    """Customer-level prediction outputs and behavioral insights."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "signals": [
                        {
                            "customer_id": "C021",
                            "loyalty_score": 0.82,
                            "churn_risk": "low",
                            "dominant_complaint_topic": "billing",
                            "feedback_sentiment": "positive"
                        }
                    ]
                }
            ]
        }
    }


class CustomerSummary(BaseModel):
    customer_id: str
    """The customer the summary is about."""

    summary: str
    """Plain English summary of customer's status and risk profile."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C021",
                    "summary": "Customer C021 has loyalty score of 0.82, low churn risk, positive recent feedback, notable complaints around billing."
                }
            ]
        }
    }


class GenerateCustomerSummaryResponse(BaseModel):
    summaries: List[CustomerSummary]
    """List of summaries for each customer."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "summaries": [
                        {
                            "customer_id": "C021",
                            "summary": "Customer C021 has loyalty score of 0.82, low churn risk, positive recent feedback, notable complaints around billing."
                        }
                    ]
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True
)


@prt.api("/generate-customer-summary", spec=api_spec)
async def run(payload: GenerateCustomerSummaryRequest, **kwargs) -> GenerateCustomerSummaryResponse:
    """
    Generates plain English summaries of individual customers based on risk and engagement data.
    """

    summaries = []

    for signal in payload.signals:
        parts = []

        if signal.loyalty_score is not None:
            parts.append(f"loyalty score of {signal.loyalty_score:.2f}")
        if signal.churn_risk:
            parts.append(f"{signal.churn_risk} churn risk")
        if signal.feedback_sentiment:
            parts.append(f"{signal.feedback_sentiment} recent feedback")
        if signal.dominant_complaint_topic:
            parts.append(f"notable complaints around {signal.dominant_complaint_topic}")

        summary = f"Customer {signal.customer_id} has " + ", ".join(parts) + "."
        summaries.append(CustomerSummary(customer_id=signal.customer_id, summary=summary))

    return GenerateCustomerSummaryResponse(summaries=summaries)

```

### apis/generate_retention_plan.py
```python
# generate_retention_plan.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List, Optional


class RetentionTarget(BaseModel):
    customer_id: str
    """ID of the customer who is at churn risk."""

    churn_risk: str
    """Level of churn risk: low, medium, or high."""

    loyalty_score: Optional[float]
    """Predicted loyalty score from the model."""

    complaint_topic: Optional[str]
    """Dominant complaint topic extracted from feedbacks."""

    sentiment: Optional[str]
    """Overall customer sentiment, if known."""

    model_config = {
        "use_attribute_docstrings": True
    }


class RetentionPlan(BaseModel):
    customer_id: str
    """ID of the customer for whom the plan is generated."""

    plan_summary: str
    """Natural language recommendation plan to retain the customer."""

    model_config = {
        "use_attribute_docstrings": True
    }


class GenerateRetentionPlanResponse(BaseModel):
    plans: List[RetentionPlan]
    """Generated action plans to reduce churn likelihood per customer."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "plans": [
                        {
                            "customer_id": "C033",
                            "plan_summary": "Customer C033 exhibits high churn risk due to support delays and negative sentiment. Recommend assigning a dedicated account manager, offering priority support, and a goodwill credit to rebuild trust."
                        }
                    ]
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    interactive=True,
    risk_profile=prt.APIRiskProfile.Medium
)


@prt.api("/generate-retention-plan", spec=api_spec)
async def run(targets: List[RetentionTarget], **kwargs) -> GenerateRetentionPlanResponse:
    """
    Creates LLM-generated retention plans based on churn risk and behavior signals.
    """

    plans = []

    for target in targets:
        recs = []

        if target.churn_risk == "high":
            recs.append("assign a dedicated account manager")
        if target.complaint_topic:
            recs.append(f"resolve recent issues around {target.complaint_topic}")
        if target.sentiment == "negative":
            recs.append("provide a goodwill gesture such as a discount or credit")
        if target.loyalty_score is not None and target.loyalty_score < 0.5:
            recs.append("initiate re-engagement campaign with personalized offers")

        plan = (
            f"Customer {target.customer_id} exhibits {target.churn_risk} churn risk"
        )
        if target.complaint_topic or target.sentiment:
            plan += f" possibly due to {target.complaint_topic or target.sentiment}"
        plan += f". Recommend to " + ", ".join(recs) + "."

        plans.append(RetentionPlan(customer_id=target.customer_id, plan_summary=plan))

    return GenerateRetentionPlanResponse(plans=plans)

```

### apis/generate_retention_risk_scores.py
```python
# apis/generate_retention_risk_scores.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List
import pandas as pd


class CustomerInteraction(BaseModel):
    customer_id: str
    """Unique identifier for the customer."""

    interaction_date: str
    """Date of the last interaction."""

    avg_sentiment: float
    """Average sentiment score across interactions."""

    total_complaints: int
    """Total number of complaints filed by the customer."""

    avg_response_time_minutes: float
    """Average response time from support team in minutes."""

    issue_resolution_rate: float
    """Percentage of resolved issues (0 to 1)."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C12345",
                    "interaction_date": "2024-05-10",
                    "avg_sentiment": -0.4,
                    "total_complaints": 3,
                    "avg_response_time_minutes": 75.0,
                    "issue_resolution_rate": 0.6
                }
            ]
        },
    }


class GenerateRiskScoresRequest(BaseModel):
    interactions: List[CustomerInteraction]
    """List of summarized interaction data per customer."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "interactions": [
                        {
                            "customer_id": "C12345",
                            "interaction_date": "2024-05-10",
                            "avg_sentiment": -0.4,
                            "total_complaints": 3,
                            "avg_response_time_minutes": 75.0,
                            "issue_resolution_rate": 0.6
                        }
                    ]
                }
            ]
        },
    }


class RiskScore(BaseModel):
    customer_id: str
    """Customer ID for which the risk is calculated."""

    risk_score: float
    """Churn risk score between 0 (low) and 1 (high)."""

    risk_level: str
    """Categorical level: Low, Medium, High."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C12345",
                    "risk_score": 0.78,
                    "risk_level": "High"
                }
            ]
        },
    }


class GenerateRiskScoresResponse(BaseModel):
    risk_scores: List[RiskScore]
    """List of churn risk scores per customer."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "risk_scores": [
                        {
                            "customer_id": "C12345",
                            "risk_score": 0.78,
                            "risk_level": "High"
                        }
                    ]
                }
            ]
        },
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    interactive=True,
    risk_profile=prt.APIRiskProfile.Low,
)


@prt.api("/generate-retention-risk-scores", spec=api_spec)
async def run(payload: GenerateRiskScoresRequest, **kwargs) -> GenerateRiskScoresResponse:
    """
    Calculates a churn risk score for each customer based on interaction sentiment,
    complaints, response time, and resolution rate.
    """
    df = pd.DataFrame([i.model_dump() for i in payload.interactions])

    # Normalize all fields between 0-1
    df["sentiment_score"] = (1 - (df["avg_sentiment"] + 1) / 2)  # more negative = higher risk
    df["complaint_score"] = df["total_complaints"] / df["total_complaints"].max()
    df["response_time_score"] = df["avg_response_time_minutes"] / df["avg_response_time_minutes"].max()
    df["resolution_score"] = 1 - df["issue_resolution_rate"]

    df["risk_score"] = (
        0.3 * df["sentiment_score"] +
        0.2 * df["complaint_score"] +
        0.2 * df["response_time_score"] +
        0.3 * df["resolution_score"]
    ).clip(0, 1)

    def categorize(score):
        if score >= 0.7:
            return "High"
        elif score >= 0.4:
            return "Medium"
        else:
            return "Low"

    results = [
        RiskScore(
            customer_id=row["customer_id"],
            risk_score=round(row["risk_score"], 2),
            risk_level=categorize(row["risk_score"])
        )
        for _, row in df.iterrows()
    ]

    return GenerateRiskScoresResponse(risk_scores=results)

```

### apis/load_customer_interaction_data.py
```python
# apis/load_customer_interaction_data.py

import practicuscore as prt
import pandas as pd
from pydantic import BaseModel
from typing import List, Optional
import os


class CustomerInteraction(BaseModel):
    customer_id: str
    """Unique identifier for the customer."""

    interaction_date: str
    """Date of the customer interaction (format: YYYY-MM-DD)."""

    channel: str
    """Communication channel used during the interaction (e.g. Email, Phone, Chat)."""

    sentiment_score: Optional[float] = None
    """Sentiment score of the interaction, ranging from -1 (very negative) to 1 (very positive)."""

    issue_type: Optional[str] = None
    """Category or type of issue raised by the customer."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C12345",
                    "interaction_date": "2024-05-10",
                    "channel": "Email",
                    "sentiment_score": -0.45,
                    "issue_type": "Billing"
                }
            ]
        },
    }


class LoadCustomerInteractionDataResponse(BaseModel):
    interactions: List[CustomerInteraction]
    """List of customer interaction records loaded from the source CSV file."""

    total_customers: int
    """Total number of unique customers found in the data."""

    total_interactions: int
    """Total number of interaction records in the dataset."""

    channels_detected: List[str]
    """List of unique interaction channels used by customers."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "interactions": [
                        {
                            "customer_id": "C12345",
                            "interaction_date": "2024-05-10",
                            "channel": "Email",
                            "sentiment_score": -0.45,
                            "issue_type": "Billing"
                        }
                    ],
                    "total_customers": 1,
                    "total_interactions": 1,
                    "channels_detected": ["Email"]
                }
            ]
        },
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=False,
)


@prt.api("/load-customer-interaction-data", spec=api_spec)
async def run(**kwargs) -> LoadCustomerInteractionDataResponse:
    """Load customer interaction records from a fixed CSV path and return structured data for analysis."""
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../customer_interactions.csv"))
    df = pd.read_csv(file_path)

    interactions = [
        CustomerInteraction(
            customer_id=row.get("customer_id", f"UNKNOWN_{i}"),
            interaction_date=row.get("interaction_date", "1970-01-01"),
            channel=row.get("channel", "Unknown"),
            sentiment_score=row.get("sentiment_score", None),
            issue_type=row.get("issue_type", "Uncategorized")
        )
        for i, row in df.iterrows()
    ]

    return LoadCustomerInteractionDataResponse(
        interactions=interactions,
        total_customers=df["customer_id"].nunique(),
        total_interactions=len(df),
        channels_detected=df["channel"].dropna().unique().tolist()
    )

```

### apis/summarize_customer_retention_case.py
```python
# apis/summarize_customer_retention_case.py
import practicuscore as prt
from pydantic import BaseModel


class SummarizeCustomerRetentionCaseRequest(BaseModel):
    customer_id: str
    """Unique identifier of the customer."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {"examples": [{"customer_id": "C105"}]},
    }


class SummarizeCustomerRetentionCaseResponse(BaseModel):
    summary: str
    """High-level summary of the customer's retention case, including risks and suggested actions."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Customer C105 has shown declining engagement and expressed dissatisfaction. Retention plan recommended."
                }
            ]
        },
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low,
)


@prt.api("/summarize-customer-retention-case", spec=api_spec)
async def run(payload: SummarizeCustomerRetentionCaseRequest, **kwargs) -> SummarizeCustomerRetentionCaseResponse:
    """
    Summarizes the current retention case for a given customer, including behavioral patterns, sentiment signals,
    and recommended actions if relevant.
    """
    return SummarizeCustomerRetentionCaseResponse(
        summary=f"Customer {payload.customer_id} has shown declining engagement and expressed dissatisfaction. Retention plan recommended."
    )

```

### apis/visualize_customer_journey_map.py
```python
# apis/visualize_customer_journey_map.py

import practicuscore as prt
from pydantic import BaseModel, Field
from typing import List, Optional


class InteractionPoint(BaseModel):
    date: str = Field(..., description="Date of the customer interaction.")
    channel: str = Field(..., description="Communication channel used (e.g., email, phone, chat).")
    sentiment_score: float = Field(..., description="Sentiment score for the interaction, from -1 (negative) to 1 (positive).")
    action_taken: Optional[str] = Field(None, description="Optional description of any action taken by the company.")

class JourneyMap(BaseModel):
    customer_id: str = Field(..., description="Unique identifier of the customer.")
    timeline: List[InteractionPoint] = Field(..., description="Chronological list of interaction points for this customer.")
    risk_flag: Optional[str] = Field(None, description="Optional churn or escalation flag for this customer.")
    recommendation: Optional[str] = Field(None, description="Summary recommendation based on the journey.")

class VisualizeCustomerJourneyRequest(BaseModel):
    customer_id: str = Field(..., description="ID of the customer whose journey should be visualized.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "customer_id": "C457"
            }
        }
    }

class VisualizeCustomerJourneyResponse(BaseModel):
    journey_map: JourneyMap = Field(..., description="Customer journey map with annotated interactions.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "journey_map": {
                    "customer_id": "C457",
                    "timeline": [
                        {
                            "date": "2024-01-10",
                            "channel": "email",
                            "sentiment_score": -0.4,
                            "action_taken": "Apology email sent"
                        },
                        {
                            "date": "2024-01-15",
                            "channel": "phone",
                            "sentiment_score": 0.1,
                            "action_taken": "Escalated to supervisor"
                        },
                        {
                            "date": "2024-01-20",
                            "channel": "chat",
                            "sentiment_score": 0.7,
                            "action_taken": "Issue resolved"
                        }
                    ],
                    "risk_flag": "Escalation",
                    "recommendation": "Maintain proactive follow-up for next 30 days."
                }
            }
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True
)


@prt.api("/visualize-customer-journey-map", spec=api_spec)
async def run(payload: VisualizeCustomerJourneyRequest) -> VisualizeCustomerJourneyResponse:
    """
    Create a structured journey map for a customer by compiling their chronological
    interaction data, sentiment trends, and key actions. This map can be used for
    visualization in dashboards or reports.

    Args:
        payload (VisualizeCustomerJourneyRequest): Contains the customer_id.

    Returns:
        VisualizeCustomerJourneyResponse: Timeline of interactions and recommendations.
    """
    # Dummy timeline for demo (in real case, fetch from DB or context)
    timeline = [
        InteractionPoint(
            date="2024-01-10",
            channel="email",
            sentiment_score=-0.4,
            action_taken="Apology email sent"
        ),
        InteractionPoint(
            date="2024-01-15",
            channel="phone",
            sentiment_score=0.1,
            action_taken="Escalated to supervisor"
        ),
        InteractionPoint(
            date="2024-01-20",
            channel="chat",
            sentiment_score=0.7,
            action_taken="Issue resolved"
        )
    ]

    return VisualizeCustomerJourneyResponse(
        journey_map=JourneyMap(
            customer_id=payload.customer_id,
            timeline=timeline,
            risk_flag="Escalation",
            recommendation="Maintain proactive follow-up for next 30 days."
        )
    )

```


---

**Previous**: [Build](../product-rec/build.md) | **Next**: [AI Assistants > AI Assistants](../../ai-assistants/ai-assistants.md)
