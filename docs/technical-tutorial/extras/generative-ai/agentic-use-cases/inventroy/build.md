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
app_name = "agentic-ai-test-inventory"
visible_name = "Agentic AI Test inventory"
description = "Test Application for Agentic AI Example inventory."
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
    "load-inventory-data/",
    "get-critical-stock-items/",
    "get-overstocked-items/",
    "get-stale-items/",
    "get-expired-items/",
    "calculate-reorder-suggestions/",
    "flag-soon-expiring-items/",
    "calculate-stock-turnover-rate/",
    "summarize-stock-health/",
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
Can you analyze the current inventory status and summarize any critical risks, such as low stock, overstocked products, expired items, or slow-moving products? Also, suggest what products might need to be reordered soon and generate a concise report.


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

### apis/calculate_reorder_suggestions.py
```python
# apis/calculate_reorder_suggestions.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List
import pandas as pd


class InventoryRecord(BaseModel):
    product_id: int
    """Unique identifier of the product."""

    product_name: str
    """Name of the product."""

    category: str
    """Product category such as 'Beverage', 'Snack', etc."""

    stock_qty: int
    """Current stock quantity available."""

    reorder_threshold: int
    """Minimum threshold to trigger a reorder."""

    max_stock: int
    """Maximum allowable stock quantity."""

    avg_daily_sales: float
    """Average daily sales calculated from historical data."""

    last_sale_date: str
    """The most recent sale date of the product (format: YYYY-MM-DD)."""

    expiry_date: str
    """The expiration date of the product (format: YYYY-MM-DD)."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": 1201,
                    "product_name": "Mineral Water",
                    "category": "Beverage",
                    "stock_qty": 25,
                    "reorder_threshold": 20,
                    "max_stock": 100,
                    "avg_daily_sales": 1.2,
                    "last_sale_date": "2025-06-25",
                    "expiry_date": "2025-09-01"
                }
            ]
        }
    }


class ReorderSuggestion(BaseModel):
    product_id: int
    """ID of the product suggested for reorder."""

    product_name: str
    """Name of the product."""

    suggested_reorder_qty: int
    """Quantity suggested to reorder."""

    reason: str
    """Reason for the reorder suggestion."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": 1201,
                    "product_name": "Mineral Water",
                    "suggested_reorder_qty": 30,
                    "reason": "Estimated to fall below reorder threshold within 7 days"
                }
            ]
        }
    }


class ReorderSuggestionsResponse(BaseModel):
    suggestions: List[ReorderSuggestion]
    """List of suggested products to reorder with estimated reorder quantities."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "suggestions": []
                }
            ]
        }
    }


class ReorderSuggestionsInput(BaseModel):
    records: List[InventoryRecord]
    """Inventory records used to calculate reorder suggestions."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "records": [
                        {
                            "product_id": 1201,
                            "product_name": "Mineral Water",
                            "category": "Beverage",
                            "stock_qty": 25,
                            "reorder_threshold": 20,
                            "max_stock": 100,
                            "avg_daily_sales": 1.2,
                            "last_sale_date": "2025-06-25",
                            "expiry_date": "2025-09-01"
                        }
                    ]
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low,
    interactive=True,
)


@prt.api("/calculate-reorder-suggestions", spec=api_spec)
async def run(request: ReorderSuggestionsInput, **kwargs) -> ReorderSuggestionsResponse:
    """Suggest products for reorder based on projected 7-day sales and reorder threshold."""
    df = pd.DataFrame([r.model_dump() for r in request.records])
    df["projected_stock"] = df["stock_qty"] - (df["avg_daily_sales"] * 7)

    reorder_df = df[df["projected_stock"] < df["reorder_threshold"]]

    suggestions = []
    for _, row in reorder_df.iterrows():
        suggested_qty = max(int((row["reorder_threshold"] * 1.5) - row["projected_stock"]), 1)
        suggestions.append(ReorderSuggestion(
            product_id=row["product_id"],
            product_name=row["product_name"],
            suggested_reorder_qty=suggested_qty,
            reason="Estimated to fall below reorder threshold within 7 days"
        ))

    return ReorderSuggestionsResponse(suggestions=suggestions)

```

### apis/calculate_stock_turnover_rate.py
```python
# apis/calculate_stock_turnover_rate.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List
import pandas as pd


class InventoryRecord(BaseModel):
    product_id: int
    """Unique identifier of the product."""

    product_name: str
    """Name of the product."""

    category: str
    """Product category such as 'Beverage', 'Snack', etc."""

    stock_qty: int
    """Current stock quantity available."""

    reorder_threshold: int
    """Minimum threshold to trigger a reorder."""

    max_stock: int
    """Maximum allowable stock quantity."""

    avg_daily_sales: float
    """Average daily sales calculated from historical data."""

    last_sale_date: str
    """The most recent sale date of the product (format: YYYY-MM-DD)."""

    expiry_date: str
    """The expiration date of the product (format: YYYY-MM-DD)."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": 1302,
                    "product_name": "Canned Corn",
                    "category": "Grocery",
                    "stock_qty": 150,
                    "reorder_threshold": 30,
                    "max_stock": 200,
                    "avg_daily_sales": 0.5,
                    "last_sale_date": "2025-06-20",
                    "expiry_date": "2026-02-01"
                }
            ]
        }
    }


class TurnoverRecord(BaseModel):
    product_id: int
    """ID of the product."""

    product_name: str
    """Name of the product."""

    turnover_rate: float
    """Calculated turnover rate (avg_daily_sales / stock_qty)."""

    risk_level: str
    """Risk classification based on turnover rate."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": 1302,
                    "product_name": "Canned Corn",
                    "turnover_rate": 0.0033,
                    "risk_level": "Low"
                }
            ]
        }
    }


class TurnoverRateResponse(BaseModel):
    low_turnover_items: List[TurnoverRecord]
    """List of products with a low stock turnover rate."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "low_turnover_items": []
                }
            ]
        }
    }


class TurnoverRateInput(BaseModel):
    records: List[InventoryRecord]
    """Inventory records to analyze turnover rates."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "records": [
                        {
                            "product_id": 1302,
                            "product_name": "Canned Corn",
                            "category": "Grocery",
                            "stock_qty": 150,
                            "reorder_threshold": 30,
                            "max_stock": 200,
                            "avg_daily_sales": 0.5,
                            "last_sale_date": "2025-06-20",
                            "expiry_date": "2026-02-01"
                        }
                    ]
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low,
    interactive=True,
)


@prt.api("/calculate-stock-turnover-rate", spec=api_spec)
async def run(request: TurnoverRateInput, **kwargs) -> TurnoverRateResponse:
    """Calculate stock turnover rate and identify products with low turnover."""
    df = pd.DataFrame([r.model_dump() for r in request.records])
    df["turnover_rate"] = df.apply(
        lambda row: round(row["avg_daily_sales"] / row["stock_qty"], 4) if row["stock_qty"] > 0 else 0.0,
        axis=1
    )

    # Define risk threshold
    low_threshold = 0.02
    low_df = df[df["turnover_rate"] < low_threshold]

    low_turnover_items = [
        TurnoverRecord(
            product_id=row["product_id"],
            product_name=row["product_name"],
            turnover_rate=row["turnover_rate"],
            risk_level="Low"
        )
        for _, row in low_df.iterrows()
    ]

    return TurnoverRateResponse(low_turnover_items=low_turnover_items)

```

### apis/flag_soon_expiring_items.py
```python
# apis/flag_soon_expiring_items.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List
import pandas as pd
from datetime import datetime, timedelta


class InventoryRecord(BaseModel):
    product_id: int
    """Unique identifier of the product."""

    product_name: str
    """Name of the product."""

    category: str
    """Product category such as 'Beverage', 'Snack', etc."""

    stock_qty: int
    """Current stock quantity available."""

    reorder_threshold: int
    """Minimum threshold to trigger a reorder."""

    max_stock: int
    """Maximum allowable stock quantity."""

    avg_daily_sales: float
    """Average daily sales calculated from historical data."""

    last_sale_date: str
    """The most recent sale date of the product (format: YYYY-MM-DD)."""

    expiry_date: str
    """The expiration date of the product (format: YYYY-MM-DD)."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": 1250,
                    "product_name": "Fresh Milk",
                    "category": "Dairy",
                    "stock_qty": 60,
                    "reorder_threshold": 25,
                    "max_stock": 120,
                    "avg_daily_sales": 3.0,
                    "last_sale_date": "2025-06-24",
                    "expiry_date": "2025-07-05"
                }
            ]
        }
    }


class SoonExpiringItemsResponse(BaseModel):
    soon_expiring_items: List[InventoryRecord]
    """List of items that will expire within the next 14 days."""

    total_soon_expiring: int
    """Total number of soon-to-expire products."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "soon_expiring_items": [],
                    "total_soon_expiring": 0
                }
            ]
        }
    }


class SoonExpiringItemsInput(BaseModel):
    records: List[InventoryRecord]
    """List of inventory items to evaluate for upcoming expiration."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "records": [
                        {
                            "product_id": 1250,
                            "product_name": "Fresh Milk",
                            "category": "Dairy",
                            "stock_qty": 60,
                            "reorder_threshold": 25,
                            "max_stock": 120,
                            "avg_daily_sales": 3.0,
                            "last_sale_date": "2025-06-24",
                            "expiry_date": "2025-07-05"
                        }
                    ]
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low,
    interactive=True,
)


@prt.api("/flag-soon-expiring-items", spec=api_spec)
async def run(request: SoonExpiringItemsInput, **kwargs) -> SoonExpiringItemsResponse:
    """Identify products that are due to expire within the next 14 days."""
    df = pd.DataFrame([r.model_dump() for r in request.records])
    df["expiry_date"] = pd.to_datetime(df["expiry_date"], errors="coerce")

    deadline = datetime.utcnow() + timedelta(days=14)
    filtered_df = df[(df["expiry_date"] >= datetime.utcnow()) & (df["expiry_date"] <= deadline)]

    soon_expiring_items = [InventoryRecord(**row) for _, row in filtered_df.iterrows()]

    return SoonExpiringItemsResponse(
        soon_expiring_items=soon_expiring_items,
        total_soon_expiring=len(soon_expiring_items)
    )

```

### apis/get_critical_stock_items.py
```python
# apis/get_critical_stock_items.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List
import pandas as pd


class InventoryRecord(BaseModel):
    product_id: int
    """Unique identifier of the product."""

    product_name: str
    """Name of the product."""

    category: str
    """Product category such as 'Beverage', 'Snack', etc."""

    stock_qty: int
    """Current stock quantity available."""

    reorder_threshold: int
    """Minimum threshold to trigger a reorder."""

    max_stock: int
    """Maximum allowable stock quantity."""

    avg_daily_sales: float
    """Average daily sales calculated from historical data."""

    last_sale_date: str
    """The most recent sale date of the product (format: YYYY-MM-DD)."""

    expiry_date: str
    """The expiration date of the product (format: YYYY-MM-DD)."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": 1001,
                    "product_name": "Apple Juice",
                    "category": "Beverage",
                    "stock_qty": 12,
                    "reorder_threshold": 20,
                    "max_stock": 150,
                    "avg_daily_sales": 3.5,
                    "last_sale_date": "2025-06-25",
                    "expiry_date": "2025-07-30"
                }
            ]
        }
    }


class CriticalStockResponse(BaseModel):
    critical_items: List[InventoryRecord]
    """List of items with stock quantity below their reorder threshold."""

    total_critical: int
    """Total number of products found to be understocked."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "critical_items": [],
                    "total_critical": 0
                }
            ]
        }
    }


class CriticalStockInput(BaseModel):
    records: List[InventoryRecord]
    """Inventory records to analyze for critical stock levels."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "records": [
                        {
                            "product_id": 1001,
                            "product_name": "Apple Juice",
                            "category": "Beverage",
                            "stock_qty": 12,
                            "reorder_threshold": 20,
                            "max_stock": 150,
                            "avg_daily_sales": 3.5,
                            "last_sale_date": "2025-06-25",
                            "expiry_date": "2025-07-30"
                        }
                    ]
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low,
    interactive=True,
)


@prt.api("/get-critical-stock-items", spec=api_spec)
async def run(request: CriticalStockInput, **kwargs) -> CriticalStockResponse:
    """Identify and return products whose stock quantity is below the reorder threshold."""
    df = pd.DataFrame([r.model_dump() for r in request.records])
    filtered_df = df[df["stock_qty"] < df["reorder_threshold"]]

    critical_items = [InventoryRecord(**row) for _, row in filtered_df.iterrows()]

    return CriticalStockResponse(
        critical_items=critical_items,
        total_critical=len(critical_items)
    )

```

### apis/get_expired_items.py
```python
# apis/get_expired_items.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List
import pandas as pd
from datetime import datetime


class InventoryRecord(BaseModel):
    product_id: int
    """Unique identifier of the product."""

    product_name: str
    """Name of the product."""

    category: str
    """Product category such as 'Beverage', 'Snack', etc."""

    stock_qty: int
    """Current stock quantity available."""

    reorder_threshold: int
    """Minimum threshold to trigger a reorder."""

    max_stock: int
    """Maximum allowable stock quantity."""

    avg_daily_sales: float
    """Average daily sales calculated from historical data."""

    last_sale_date: str
    """The most recent sale date of the product (format: YYYY-MM-DD)."""

    expiry_date: str
    """The expiration date of the product (format: YYYY-MM-DD)."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": 1100,
                    "product_name": "Yogurt",
                    "category": "Dairy",
                    "stock_qty": 40,
                    "reorder_threshold": 20,
                    "max_stock": 100,
                    "avg_daily_sales": 2.2,
                    "last_sale_date": "2025-06-24",
                    "expiry_date": "2025-06-15"
                }
            ]
        }
    }


class ExpiredItemsResponse(BaseModel):
    expired_items: List[InventoryRecord]
    """List of products whose expiration date has already passed."""

    total_expired: int
    """Total number of expired products detected."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "expired_items": [],
                    "total_expired": 0
                }
            ]
        }
    }


class ExpiredItemsInput(BaseModel):
    records: List[InventoryRecord]
    """Inventory records to analyze for expiration status."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "records": [
                        {
                            "product_id": 1100,
                            "product_name": "Yogurt",
                            "category": "Dairy",
                            "stock_qty": 40,
                            "reorder_threshold": 20,
                            "max_stock": 100,
                            "avg_daily_sales": 2.2,
                            "last_sale_date": "2025-06-24",
                            "expiry_date": "2025-06-15"
                        }
                    ]
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low,
    interactive=True,
)


@prt.api("/get-expired-items", spec=api_spec)
async def run(request: ExpiredItemsInput, **kwargs) -> ExpiredItemsResponse:
    """Detect expired products based on their expiration date."""
    df = pd.DataFrame([r.model_dump() for r in request.records])
    df["expiry_date"] = pd.to_datetime(df["expiry_date"], errors="coerce")

    today = datetime.utcnow()
    expired_df = df[df["expiry_date"] < today]

    expired_items = [InventoryRecord(**row) for _, row in expired_df.iterrows()]

    return ExpiredItemsResponse(
        expired_items=expired_items,
        total_expired=len(expired_items)
    )

```

### apis/get_overstocked_items.py
```python
# apis/get_overstocked_items.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List
import pandas as pd


class InventoryRecord(BaseModel):
    product_id: int
    """Unique identifier of the product."""

    product_name: str
    """Name of the product."""

    category: str
    """Product category such as 'Beverage', 'Snack', etc."""

    stock_qty: int
    """Current stock quantity available."""

    reorder_threshold: int
    """Minimum threshold to trigger a reorder."""

    max_stock: int
    """Maximum allowable stock quantity."""

    avg_daily_sales: float
    """Average daily sales calculated from historical data."""

    last_sale_date: str
    """The most recent sale date of the product (format: YYYY-MM-DD)."""

    expiry_date: str
    """The expiration date of the product (format: YYYY-MM-DD)."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": 1050,
                    "product_name": "Chocolate",
                    "category": "Snack",
                    "stock_qty": 220,
                    "reorder_threshold": 30,
                    "max_stock": 150,
                    "avg_daily_sales": 1.5,
                    "last_sale_date": "2025-06-22",
                    "expiry_date": "2025-08-01"
                }
            ]
        }
    }


class OverstockedItemsResponse(BaseModel):
    overstocked_items: List[InventoryRecord]
    """List of items with stock quantity above the maximum allowable stock."""

    total_overstocked: int
    """Total number of overstocked products detected."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "overstocked_items": [],
                    "total_overstocked": 0
                }
            ]
        }
    }


class OverstockedItemsInput(BaseModel):
    records: List[InventoryRecord]
    """Inventory records to analyze for overstocked status."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "records": [
                        {
                            "product_id": 1050,
                            "product_name": "Chocolate",
                            "category": "Snack",
                            "stock_qty": 220,
                            "reorder_threshold": 30,
                            "max_stock": 150,
                            "avg_daily_sales": 1.5,
                            "last_sale_date": "2025-06-22",
                            "expiry_date": "2025-08-01"
                        }
                    ]
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low,
    interactive=True,
)


@prt.api("/get-overstocked-items", spec=api_spec)
async def run(request: OverstockedItemsInput, **kwargs) -> OverstockedItemsResponse:
    """Identify and return products whose stock quantity exceeds their maximum stock limit."""
    df = pd.DataFrame([r.model_dump() for r in request.records])
    filtered_df = df[df["stock_qty"] > df["max_stock"]]

    overstocked_items = [InventoryRecord(**row) for _, row in filtered_df.iterrows()]

    return OverstockedItemsResponse(
        overstocked_items=overstocked_items,
        total_overstocked=len(overstocked_items)
    )

```

### apis/get_stale_items.py
```python
# apis/get_stale_items.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List
import pandas as pd
from datetime import datetime, timedelta


class InventoryRecord(BaseModel):
    product_id: int
    """Unique identifier of the product."""

    product_name: str
    """Name of the product."""

    category: str
    """Product category such as 'Beverage', 'Snack', etc."""

    stock_qty: int
    """Current stock quantity available."""

    reorder_threshold: int
    """Minimum threshold to trigger a reorder."""

    max_stock: int
    """Maximum allowable stock quantity."""

    avg_daily_sales: float
    """Average daily sales calculated from historical data."""

    last_sale_date: str
    """The most recent sale date of the product (format: YYYY-MM-DD)."""

    expiry_date: str
    """The expiration date of the product (format: YYYY-MM-DD)."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": 1088,
                    "product_name": "Peach Juice",
                    "category": "Beverage",
                    "stock_qty": 50,
                    "reorder_threshold": 15,
                    "max_stock": 120,
                    "avg_daily_sales": 0.3,
                    "last_sale_date": "2025-04-15",
                    "expiry_date": "2025-07-10"
                }
            ]
        }
    }


class StaleItemsResponse(BaseModel):
    stale_items: List[InventoryRecord]
    """List of products that have not been sold in the last 30 days."""

    total_stale: int
    """Total number of stale products detected."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "stale_items": [],
                    "total_stale": 0
                }
            ]
        }
    }


class StaleItemsInput(BaseModel):
    records: List[InventoryRecord]
    """Inventory records to analyze for stale items (not sold in the last 30 days)."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "records": [
                        {
                            "product_id": 1088,
                            "product_name": "Peach Juice",
                            "category": "Beverage",
                            "stock_qty": 50,
                            "reorder_threshold": 15,
                            "max_stock": 120,
                            "avg_daily_sales": 0.3,
                            "last_sale_date": "2025-04-15",
                            "expiry_date": "2025-07-10"
                        }
                    ]
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low,
    interactive=True,
)


@prt.api("/get-stale-items", spec=api_spec)
async def run(request: StaleItemsInput, **kwargs) -> StaleItemsResponse:
    """Detect products with no recorded sales in the last 30 days."""
    df = pd.DataFrame([r.model_dump() for r in request.records])
    df["last_sale_date"] = pd.to_datetime(df["last_sale_date"], errors="coerce")

    threshold_date = datetime.utcnow() - timedelta(days=30)
    filtered_df = df[df["last_sale_date"] < threshold_date]

    stale_items = [InventoryRecord(**row) for _, row in filtered_df.iterrows()]

    return StaleItemsResponse(
        stale_items=stale_items,
        total_stale=len(stale_items)
    )

```

### apis/load_inventory_data.py
```python
# apis/load_inventory_data.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List
import pandas as pd
import os


class InventoryRecord(BaseModel):
    product_id: int
    """Unique identifier of the product."""

    product_name: str
    """Name of the product."""

    category: str
    """Product category such as 'Beverage', 'Snack', etc."""

    stock_qty: int
    """Current stock quantity available."""

    reorder_threshold: int
    """Minimum threshold to trigger a reorder."""

    max_stock: int
    """Maximum allowable stock quantity."""

    avg_daily_sales: float
    """Average daily sales calculated from historical data."""

    last_sale_date: str
    """The most recent sale date of the product (format: YYYY-MM-DD)."""

    expiry_date: str
    """The expiration date of the product (format: YYYY-MM-DD)."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": 1001,
                    "product_name": "Apple Juice",
                    "category": "Beverage",
                    "stock_qty": 12,
                    "reorder_threshold": 20,
                    "max_stock": 150,
                    "avg_daily_sales": 3.5,
                    "last_sale_date": "2025-06-25",
                    "expiry_date": "2025-07-30"
                }
            ]
        }
    }


class LoadInventoryDataResponse(BaseModel):
    records: List[InventoryRecord]
    """List of inventory records extracted from the source CSV file."""

    total_products: int
    """Total number of product entries found in the data."""

    expired_items: int
    """Number of products with expiration date already passed."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "records": [],
                    "total_products": 100,
                    "expired_items": 3
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low,
    interactive=True,
)


@prt.api("/load-inventory-data", spec=api_spec)
async def run(**kwargs) -> LoadInventoryDataResponse:
    """Load inventory data from a fixed CSV path and return structured inventory records."""
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../inventory_data.csv"))
    df = pd.read_csv(file_path)

    df["expiry_date"] = pd.to_datetime(df["expiry_date"], errors="coerce")
    today = pd.Timestamp.today()

    records = [InventoryRecord(**row) for _, row in df.iterrows()]
    expired_count = df[df["expiry_date"] < today].shape[0]

    return LoadInventoryDataResponse(
        records=records,
        total_products=len(df),
        expired_items=expired_count
    )

```

### apis/summarize_stock_health.py
```python
# apis/summarize_stock_health.py

import practicuscore as prt
from pydantic import BaseModel, Field


class SummaryRequest(BaseModel):
    critical_count: int = Field(..., description="Number of products with stock below reorder threshold")
    overstocked_count: int = Field(..., description="Number of products with stock above max limit")
    stale_count: int = Field(..., description="Number of products with no sales in the last 30 days")
    expired_count: int = Field(..., description="Number of expired products")

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "critical_count": 3,
                    "overstocked_count": 5,
                    "stale_count": 2,
                    "expired_count": 1
                }
            ]
        }
    }


class StockHealthSummary(BaseModel):
    summary: str
    """A natural language summary describing the current stock health situation."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "There are 3 critical items requiring immediate restock. 5 products are overstocked, suggesting excess inventory. 2 products have had no sales in the last 30 days. 1 product is expired and must be removed from stock."
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low,
    interactive=True,
)


@prt.api("/summarize-stock-health", spec=api_spec)
async def run(request: SummaryRequest) -> StockHealthSummary:
    """Generate a summary statement based on the given inventory analysis counts."""
    parts = []

    if request.critical_count > 0:
        parts.append(f"{request.critical_count} critical item(s) require immediate restocking")
    if request.overstocked_count > 0:
        parts.append(f"{request.overstocked_count} item(s) are overstocked and may need clearance")
    if request.stale_count > 0:
        parts.append(f"{request.stale_count} item(s) have had no sales in the last 30 days")
    if request.expired_count > 0:
        parts.append(f"{request.expired_count} expired item(s) must be removed from inventory")

    if not parts:
        summary = "Inventory levels are healthy. No critical issues detected."
    else:
        summary = ". ".join(parts) + "."

    return StockHealthSummary(summary=summary)

```


---

**Previous**: [Build](../hr/build.md) | **Next**: [Langflow Apis > Langflow API](../../langflow-apis/langflow-api.md)
