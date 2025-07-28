---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.6
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
app_name = "agentic-ai-test-recommendation"
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
    "analyze-product-preferences/",
    "load-customer-profile-data/",
    "predict-product-eligibility/",
    "score-bundle-affinity/",
    "suggest-dynamic-product-bundle/",
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
Based on our customer profiles, segment the users and recommend personalized products for each segment.
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

### apis/analyze_product_preferences.py
```python
import practicuscore as prt
from pydantic import BaseModel
from typing import List, Dict
from collections import Counter


class CustomerProfile(BaseModel):
    customer_id: str
    """Unique identifier for the customer."""

    past_purchases: List[str]
    """List of product categories previously purchased."""


class AnalyzePreferencesRequest(BaseModel):
    customers: List[CustomerProfile]
    """List of customer profiles including purchase history."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customers": [
                        {
                            "customer_id": "C001",
                            "past_purchases": ["Electronics", "Books", "Electronics"]
                        },
                        {
                            "customer_id": "C002",
                            "past_purchases": ["Beauty", "Books"]
                        }
                    ]
                }
            ]
        }
    }


class PreferenceStats(BaseModel):
    category: str
    """Name of the product category."""

    count: int
    """How many times this category appeared across all customers."""


class AnalyzePreferencesResponse(BaseModel):
    preferences: List[PreferenceStats]
    """Aggregated product preference statistics."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "preferences": [
                        {"category": "Electronics", "count": 2},
                        {"category": "Books", "count": 2},
                        {"category": "Beauty", "count": 1}
                    ]
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    interactive=False,
    risk_profile=prt.APIRiskProfile.Low
)


@prt.api("/analyze-product-preferences", spec=api_spec)
async def run(payload: AnalyzePreferencesRequest, **kwargs) -> AnalyzePreferencesResponse:
    """
    Aggregates past purchase categories to determine overall product preferences
    across the customer base.
    """
    category_counter = Counter()
    for customer in payload.customers:
        category_counter.update(customer.past_purchases)

    results = [
        PreferenceStats(category=cat, count=count)
        for cat, count in category_counter.most_common()
    ]

    return AnalyzePreferencesResponse(preferences=results)

```

### apis/load_customer_profile_data.py
```python
import practicuscore as prt
from pydantic import BaseModel
from typing import List
import pandas as pd
import os


class CustomerProfile(BaseModel):
    customer_id: str
    """Unique identifier for the customer."""

    age: int
    """Age of the customer."""

    gender: str
    """Gender of the customer."""

    location: str
    """Location or region."""

    total_purchases: int
    """Number of past purchases."""

    average_spend: float
    """Average spend per purchase."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C001",
                    "age": 29,
                    "gender": "Male",
                    "location": "Istanbul",
                    "total_purchases": 12,
                    "average_spend": 78.5
                }
            ]
        }
    }


class LoadCustomerProfileDataResponse(BaseModel):
    customers: List[CustomerProfile]
    """List of structured customer profile records."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": {
                "customers": [
                    {
                        "customer_id": "C001",
                        "age": 29,
                        "gender": "Male",
                        "location": "Istanbul",
                        "total_purchases": 12,
                        "average_spend": 78.5
                    }
                ]
            }
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    interactive=True,
    risk_profile=prt.APIRiskProfile.Low
)


@prt.api("/load-customer-profile-data", spec=api_spec)
async def run(**kwargs) -> LoadCustomerProfileDataResponse:
    """
    Loads structured customer profile data from a CSV file located in the parent directory.
    """
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../customer_profiles.csv"))
    df = pd.read_csv(file_path)

    customers = [
        CustomerProfile(
            customer_id=str(row["customer_id"]),
            age=int(row["age"]),
            gender=row["gender"],
            location=row["location"],
            total_purchases=int(row["total_purchases"]),
            average_spend=float(row["average_spend"])
        )
        for _, row in df.iterrows()
    ]

    return LoadCustomerProfileDataResponse(customers=customers)

```

### apis/predict_product_eligibility.py
```python
import practicuscore as prt
from pydantic import BaseModel
from typing import List, Optional


class CustomerProfile(BaseModel):
    customer_id: str
    """Unique customer identifier."""

    age: int
    """Age of the customer."""

    gender: str
    """Gender of the customer (e.g., Male, Female)."""

    location: str
    """Customer's region or city."""

    total_purchases: int
    """Number of purchases the customer has made."""

    average_spend: float
    """Average amount the customer spends."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C019",
                    "age": 34,
                    "gender": "Male",
                    "location": "Istanbul",
                    "total_purchases": 12,
                    "average_spend": 84.5
                }
            ]
        }
    }


class PredictEligibilityRequest(BaseModel):
    product_name: str
    """Name of the product to check eligibility for."""

    candidates: List[CustomerProfile]
    """List of customer profiles to check."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "product_name": "SmartFitness Tracker",
                    "candidates": [
                        {
                            "customer_id": "C019",
                            "age": 34,
                            "gender": "Male",
                            "location": "Istanbul",
                            "total_purchases": 12,
                            "average_spend": 84.5
                        }
                    ]
                }
            ]
        }
    }


class EligibilityPrediction(BaseModel):
    customer_id: str
    """ID of the customer."""

    is_eligible: bool
    """Whether the customer is eligible for the product."""

    reasoning: str
    """Explanation of the eligibility decision."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C019",
                    "is_eligible": True,
                    "reasoning": "Customer has consistent spend above 80 and more than 10 purchases. Good candidate for SmartFitness Tracker."
                }
            ]
        }
    }


class PredictEligibilityResponse(BaseModel):
    results: List[EligibilityPrediction]
    """Eligibility prediction results for each customer."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "results": [
                        {
                            "customer_id": "C019",
                            "is_eligible": True,
                            "reasoning": "Customer has consistent spend above 80 and more than 10 purchases. Good candidate for SmartFitness Tracker."
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


@prt.api("/predict-product-eligibility", spec=api_spec)
async def run(payload: PredictEligibilityRequest, **kwargs) -> PredictEligibilityResponse:
    """
    Predicts product eligibility for each customer based on profile metrics.
    """

    results = []

    for c in payload.candidates:
        if c.average_spend > 70 and c.total_purchases > 5:
            eligible = True
            reasoning = f"Customer has consistent spend above 70 and more than 5 purchases. Good candidate for {payload.product_name}."
        else:
            eligible = False
            reasoning = f"Customer has insufficient purchase history or low average spend. Not a strong candidate for {payload.product_name}."

        results.append(EligibilityPrediction(
            customer_id=c.customer_id,
            is_eligible=eligible,
            reasoning=reasoning
        ))

    return PredictEligibilityResponse(results=results)

```

### apis/score_bundle_affinity.py
```python
import practicuscore as prt
from pydantic import BaseModel
from typing import List


class ProductBundle(BaseModel):
    customer_id: str
    """Unique customer identifier."""

    proposed_bundle: List[str]
    """List of proposed product names in the bundle."""

    past_purchases: List[str]
    """List of past product names the customer has bought."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C022",
                    "proposed_bundle": ["Mouse Pad", "USB-C Hub"],
                    "past_purchases": ["Wireless Mouse", "Laptop Stand"]
                }
            ]
        }
    }


class ScoreBundleAffinityRequest(BaseModel):
    bundles: List[ProductBundle]
    """List of customer bundles to score based on affinity."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "bundles": [
                        {
                            "customer_id": "C022",
                            "proposed_bundle": ["Mouse Pad", "USB-C Hub"],
                            "past_purchases": ["Wireless Mouse", "Laptop Stand"]
                        }
                    ]
                }
            ]
        }
    }


class BundleAffinityScore(BaseModel):
    customer_id: str
    """Customer ID."""

    affinity_score: float
    """Affinity score (0.0 to 1.0) indicating relevance of the product bundle."""

    reason: str
    """Explanation for the score based on overlap or similarity."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C022",
                    "affinity_score": 0.75,
                    "reason": "Partial overlap with prior purchases (Wireless Mouse)."
                }
            ]
        }
    }


class ScoreBundleAffinityResponse(BaseModel):
    scores: List[BundleAffinityScore]
    """List of affinity scores per customer bundle."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "scores": [
                        {
                            "customer_id": "C022",
                            "affinity_score": 0.75,
                            "reason": "Partial overlap with prior purchases (Wireless Mouse)."
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


@prt.api("/score-bundle-affinity", spec=api_spec)
async def run(payload: ScoreBundleAffinityRequest, **kwargs) -> ScoreBundleAffinityResponse:
    """
    Scores the affinity of each proposed product bundle based on the customer's past purchases.
    Higher scores reflect greater similarity or complementarity.
    """
    results = []

    for item in payload.bundles:
        past = set([p.lower() for p in item.past_purchases])
        proposed = set([p.lower() for p in item.proposed_bundle])
        intersection = past.intersection(proposed)

        if not item.past_purchases:
            score = 0.0
            reason = "No past purchases to compare."
        else:
            score = len(intersection) / len(item.proposed_bundle) if item.proposed_bundle else 0.0
            reason = f"{'Partial' if 0 < score < 1 else 'Full' if score == 1 else 'No'} overlap with prior purchases."

        results.append(BundleAffinityScore(
            customer_id=item.customer_id,
            affinity_score=round(score, 2),
            reason=reason
        ))

    return ScoreBundleAffinityResponse(scores=results)

```

### apis/suggest_dynamic_product_bundle.py
```python
import practicuscore as prt
from pydantic import BaseModel
from typing import List, Dict


class PurchaseHistory(BaseModel):
    customer_id: str
    """Unique customer ID."""

    previous_products: List[str]
    """List of previously purchased product names."""

    total_spend: float
    """Total amount spent by the customer."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C019",
                    "previous_products": ["Wireless Mouse", "Laptop Stand", "Keyboard"],
                    "total_spend": 320.5
                }
            ]
        }
    }


class SuggestBundleRequest(BaseModel):
    histories: List[PurchaseHistory]
    """List of customer purchase histories."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "histories": [
                        {
                            "customer_id": "C019",
                            "previous_products": ["Wireless Mouse", "Laptop Stand", "Keyboard"],
                            "total_spend": 320.5
                        }
                    ]
                }
            ]
        }
    }


class BundleSuggestion(BaseModel):
    customer_id: str
    """Customer ID."""

    recommended_bundle: List[str]
    """List of suggested products as a dynamic bundle."""

    reason: str
    """Reason for suggesting this bundle."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C019",
                    "recommended_bundle": ["Bluetooth Headphones", "USB Hub"],
                    "reason": "Customer previously purchased work-from-home accessories. Recommended complementary items."
                }
            ]
        }
    }


class SuggestBundleResponse(BaseModel):
    suggestions: List[BundleSuggestion]
    """List of dynamic product bundle suggestions per customer."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "suggestions": [
                        {
                            "customer_id": "C019",
                            "recommended_bundle": ["Bluetooth Headphones", "USB Hub"],
                            "reason": "Customer previously purchased work-from-home accessories. Recommended complementary items."
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


@prt.api("/suggest-dynamic-product-bundle", spec=api_spec)
async def run(payload: SuggestBundleRequest, **kwargs) -> SuggestBundleResponse:
    """
    Suggests product bundles dynamically based on customer purchase history.
    """

    bundle_db = {
        "Laptop Stand": ["USB-C Hub", "Laptop Sleeve"],
        "Wireless Mouse": ["Mouse Pad", "Keyboard"],
        "Keyboard": ["Wrist Rest", "Monitor Riser"],
        "Smartphone Case": ["Screen Protector", "Phone Grip"],
        "Yoga Mat": ["Resistance Bands", "Foam Roller"]
    }

    suggestions = []

    for h in payload.histories:
        recommended = []
        reasons = []

        for item in h.previous_products:
            if item in bundle_db:
                recommended.extend(bundle_db[item])
                reasons.append(f"Related to previous purchase: {item}")

        unique_recommended = list(set(recommended))
        reason_text = " | ".join(reasons) if reasons else "Based on previous purchase categories."

        suggestions.append(BundleSuggestion(
            customer_id=h.customer_id,
            recommended_bundle=unique_recommended,
            reason=reason_text
        ))

    return SuggestBundleResponse(suggestions=suggestions)

```


---

**Previous**: [Milvus Chain](../../milvus-embedding-and-langchain/milvus-chain.md) | **Next**: [Growth Strategist > Build](../growth-strategist/build.md)
