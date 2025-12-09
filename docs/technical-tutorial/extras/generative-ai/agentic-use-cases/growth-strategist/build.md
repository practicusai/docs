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
app_name = "agentic-ai-test-sales"
visible_name = "Agentic AI Test SALES"
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
    "bootstrap-data/",
    "analyze-sales-trends/",
    "detect-regional-drop/",
    "top-products-insight/",
    "predict-growth-opportunities/",
    "generate-campaign-idea/",
    "suggest-target-audience/",
    "generate-marketing-slogan/",
    "sentiment-test-slogan/",
    "validate-campaign-json/",
    "generate-social-posts/",
    "generate-strategic-summary/",
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
Analyze my sales trends and suggest where I should focus to grow. Then create a campaign idea for it.
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

### apis/analyze_sales_trends.py
```python
# apis/analyze_sales_trends.py
import practicuscore as prt
from pydantic import BaseModel
from typing import List, Literal
from datetime import datetime, timezone


class SalesTrendSummary(BaseModel):
    trend_direction: Literal["increasing", "decreasing", "stable"]
    """Overall direction of sales trend"""

    peak_day: str
    """Day with the highest sales, in YYYY-MM-DD format"""


class SalesRecord(BaseModel):
    date: datetime
    """The date of the sales transaction in UTC format."""

    product: str
    """The name of the product sold."""

    region: str
    """The geographical region where the sale occurred."""

    units_sold: int
    """The number of product units sold."""

    revenue: float
    """The total revenue generated from this sale."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "date": "2024-12-01T00:00:00Z",
                    "product": "Laptop",
                    "region": "Asia",
                    "units_sold": 120,
                    "revenue": 120000.0
                }
            ]
        }
    }


class AnalyzeSalesTrendsRequest(BaseModel):
    sales_data: List[SalesRecord]
    """List of sales records to analyze."""

    start_date: datetime
    """The start date of the period to be analyzed, in UTC."""

    end_date: datetime
    """The end date of the period to be analyzed, in UTC."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "sales_data": [
                        {
                            "date": "2024-12-01T00:00:00Z",
                            "product": "Laptop",
                            "region": "Asia",
                            "units_sold": 120,
                            "revenue": 120000.0
                        }
                    ],
                    "start_date": "2024-12-01T00:00:00Z",
                    "end_date": "2024-12-31T00:00:00Z"
                }
            ]
        }
    }


class AnalyzeSalesTrendsResponse(BaseModel):
    total_units: int
    """Total number of units sold in the analyzed period."""

    total_revenue: float
    """Total revenue generated in the analyzed period."""

    daily_average_units: float
    """Average number of units sold per day."""

    trend_summary: SalesTrendSummary
    """Summary of trend direction and peak day."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "total_units": 30500,
                    "total_revenue": 15200000.0,
                    "daily_average_units": 492.06,
                    "trend_summary": {
                        "trend_direction": "increasing",
                        "peak_day": "2025-01-10"
                    }
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
)


@prt.api("/analyze-sales-trends", spec=api_spec)
async def run(payload: AnalyzeSalesTrendsRequest, **kwargs) -> AnalyzeSalesTrendsResponse:
    """
    Analyze overall sales performance for a selected date range V19.
    Provides total units sold, revenue, daily averages, trend direction and peak day.
    """

    try:
        def make_utc(dt: datetime) -> datetime:
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)

        start_date = make_utc(payload.start_date)
        end_date = make_utc(payload.end_date)

        filtered = [
            record for record in payload.sales_data
            if start_date <= make_utc(record.date) <= end_date
        ]

        if not filtered:
            return AnalyzeSalesTrendsResponse(
                total_units=0,
                total_revenue=0.0,
                daily_average_units=0.0,
                trend_summary=SalesTrendSummary(
                    trend_direction="stable",
                    peak_day="N/A"
                )
            )

        filtered.sort(key=lambda x: x.date)

        total_units = sum(r.units_sold for r in filtered)
        total_revenue = sum(r.revenue for r in filtered)
        num_days = (end_date - start_date).days + 1
        daily_avg = total_units / num_days if num_days else 0

        first_avg = sum(r.units_sold for r in filtered[:5]) / 5
        last_avg = sum(r.units_sold for r in filtered[-5:]) / 5

        if last_avg > first_avg * 1.1:
            trend = "increasing"
        elif last_avg < first_avg * 0.9:
            trend = "decreasing"
        else:
            trend = "stable"

        day_totals = {}
        for r in filtered:
            dt = make_utc(r.date)
            day_totals.setdefault(dt, 0)
            day_totals[dt] += r.units_sold
        peak_day = max(day_totals, key=day_totals.get).strftime("%Y-%m-%d")

        return AnalyzeSalesTrendsResponse(
            total_units=total_units,
            total_revenue=total_revenue,
            daily_average_units=round(daily_avg, 2),
            trend_summary={
                "trend_direction": trend,
                "peak_day": peak_day
            }
        )

    except Exception as e:
        prt.logger.error(f"[analyze-sales-trends] Exception: {e}")
        raise

```

### apis/bootstrap_data.py
```python
# apis/bootstrap_data.py
import practicuscore as prt
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
import random

class SalesRecord(BaseModel):
    date: datetime
    """Date of the sale."""

    product: str
    """Product name."""

    region: str
    """Sales region."""

    units_sold: int
    """Number of units sold."""

    revenue: float
    """Revenue from the sale."""

class BootstrapDataRequest(BaseModel):
    """Empty request for bootstrap data loading."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [{}]
        }
    }


class BootstrapDataResponse(BaseModel):
    sales_data: List[SalesRecord]
    """Predefined static list of 100 sales records."""

    model_config = {
        "use_attribute_docstrings": True
    }

api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low
)


@prt.api("/bootstrap-data", spec=api_spec)
async def run(payload: BootstrapDataRequest, **kwargs) -> BootstrapDataResponse:
    """
    Load a static dataset of 100 predefined sales records into the agent's context.
    This tool should be invoked at the start of any agent flow.
    """
    products = ["Laptop", "Monitor", "Tablet"]
    regions = ["Asia", "Europe", "North America"]
    base_date = datetime(2025, 1, 1)

    static_data = []

    random.seed(42) 

    for i in range(10):  
        product = random.choice(products)
        region = random.choice(regions)
        date = base_date + timedelta(days=i % 30)
        units_sold = random.randint(20, 150)
        unit_price = {
            "Laptop": 1000,
            "Monitor": 500,
            "Tablet": 400
        }[product]
        revenue = units_sold * unit_price

        static_data.append(SalesRecord(
            date=date,
            product=product,
            region=region,
            units_sold=units_sold,
            revenue=revenue
        ))

    return BootstrapDataResponse(sales_data=static_data)

```

### apis/detect_regional_drop.py
```python
# apis/detect_regional_drop.py
import practicuscore as prt
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from collections import defaultdict


class SalesRecord(BaseModel):
    date: datetime
    """The UTC date when the sale was recorded."""

    product: str
    """The name of the product sold."""

    region: str
    """The geographical region where the product was sold."""

    units_sold: int
    """The number of units sold in this transaction."""

    revenue: float
    """The total revenue generated from the sale."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "date": "2024-12-01T00:00:00Z",
                    "product": "Monitor",
                    "region": "Asia",
                    "units_sold": 150,
                    "revenue": 45000.0
                }
            ]
        }
    }


class DetectRegionalDropRequest(BaseModel):
    sales_data: List[SalesRecord]
    """List of sales transactions to analyze."""

    start_date: datetime
    """Start date of the analysis window (UTC)."""

    end_date: datetime
    """End date of the analysis window (UTC)."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "sales_data": [
                        {
                            "date": "2024-12-01T00:00:00Z",
                            "product": "Monitor",
                            "region": "Asia",
                            "units_sold": 150,
                            "revenue": 45000.0
                        }
                    ],
                    "start_date": "2024-12-01T00:00:00Z",
                    "end_date": "2025-02-28T00:00:00Z"
                }
            ]
        }
    }


class RegionalDrop(BaseModel):
    region: str
    """Region where the sales drop was detected."""

    product: str
    """Product that showed a decrease in sales."""

    drop_percentage: float
    """Percentage of decline in units sold between the two periods."""

    comment: Optional[str]
    """Optional explanation or context about the decline."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "region": "Asia",
                    "product": "Monitor",
                    "drop_percentage": 42.5,
                    "comment": "Sales declined sharply compared to the previous period."
                }
            ]
        }
    }


class DetectRegionalDropResponse(BaseModel):
    drops: List[RegionalDrop]
    """List of regional product drops with percentage and commentary."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "drops": [
                        {
                            "region": "Asia",
                            "product": "Monitor",
                            "drop_percentage": 42.5,
                            "comment": "Sales declined sharply compared to the previous period."
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
)



@prt.api("/detect-regional-drop", spec=api_spec)
async def run(payload: DetectRegionalDropRequest, **kwargs) -> DetectRegionalDropResponse:
    """
    Detect regional drops in product sales over a selected date range.
    Compares first and second half of the period to find significant declines.
    """
    try:
        
        from datetime import timezone

        def make_utc(dt: datetime) -> datetime:
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)


        start_date = make_utc(payload.start_date)
        end_date = make_utc(payload.end_date)
        mid_point = start_date + (end_date - start_date) / 2

        current_period = defaultdict(list)
        previous_period = defaultdict(list)

        for r in payload.sales_data:
            r_date = make_utc(r.date)
            if start_date <= r_date <= mid_point:
                previous_period[(r.region, r.product)].append(r.units_sold)
            elif mid_point < r_date <= end_date:
                current_period[(r.region, r.product)].append(r.units_sold)

        drops = []
        for key in previous_period:
            prev_avg = sum(previous_period[key]) / len(previous_period[key]) if previous_period[key] else 0
            curr_avg = sum(current_period.get(key, [])) / len(current_period.get(key, [])) if current_period.get(key) else 0

            if prev_avg > 0 and curr_avg < prev_avg * 0.85:
                drop_pct = round((prev_avg - curr_avg) / prev_avg * 100, 2)
                drops.append(RegionalDrop(
                    region=key[0],
                    product=key[1],
                    drop_percentage=drop_pct,
                    comment="Sales declined sharply compared to the previous period."
                ))

        return DetectRegionalDropResponse(drops=drops)

    except Exception as e:
        prt.logger.error(f"[detect-regional-drop] Exception: {e}")
        raise

```

### apis/generate_campaign_idea.py
```python
# apis/generate_campaign_idea.py
import practicuscore as prt
from pydantic import BaseModel
from typing import List


class GrowthOpportunity(BaseModel):
    product: str
    """The product that represents a growth opportunity."""

    region: str
    """The region where this product shows growth potential."""

    reason: str
    """Explanation of why this product-region combination is promising."""

    confidence: str
    """Confidence level of the opportunity (e.g., high, medium, low)."""


class GenerateCampaignIdeaRequest(BaseModel):
    goal: str
    """The business goal in natural language (e.g., increase monitor sales in Asia by 20%)."""

    opportunities: List[GrowthOpportunity]
    """A list of previously identified product-region growth opportunities."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "goal": "Increase monitor sales in Asia by 20% in Q1",
                    "opportunities": [
                        {
                            "product": "Monitor",
                            "region": "Asia",
                            "reason": "Strong market potential with recent positive sales trend.",
                            "confidence": "high"
                        }
                    ]
                }
            ]
        }
    }


class GenerateCampaignIdeaResponse(BaseModel):
    campaign_name: str
    """A short and catchy name for the proposed marketing campaign."""

    description: str
    """A one-paragraph summary of what the campaign aims to achieve."""

    strategy: str
    """A suggested strategic approach to achieve the campaign's goal."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "campaign_name": "Focus Asia 20",
                    "description": "A regional campaign to boost monitor sales by highlighting productivity and affordability.",
                    "strategy": "Use targeted ads on professional networks and bundled discounts for remote workers."
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=False,
    risk_profile=prt.APIRiskProfile.Medium,
)


@prt.api("/generate-campaign-idea", spec=api_spec)
async def run(payload: GenerateCampaignIdeaRequest, **kwargs) -> GenerateCampaignIdeaResponse:
    """
    Generate a marketing campaign plan based on a defined business goal and a list of growth opportunities.

    Use this tool when a user provides a clear objective and market insights,
    and needs help forming a compelling campaign concept.

    The input includes a business goal and opportunity details (product, region, reason, confidence).
    The output includes a campaign name, high-level description, and suggested strategy.
    This tool supports decision-making for sales and marketing initiatives.
    """

    goal = payload.goal
    product_names = [op.product for op in payload.opportunities]
    region_names = [op.region for op in payload.opportunities]

    campaign_name = f"{product_names[0]} Boost in {region_names[0]}"
    description = f"This campaign focuses on growing {product_names[0]} sales in {region_names[0]}, supporting the goal: '{goal}'."
    strategy = f"Leverage digital ads and local influencers in {region_names[0]}. Highlight features that align with productivity and affordability."

    return GenerateCampaignIdeaResponse(
        campaign_name=campaign_name,
        description=description,
        strategy=strategy
    )

```

### apis/generate_marketing_slogan.py
```python
# apis/generate_marketing_slogan.py
import practicuscore as prt
from pydantic import BaseModel
from typing import List


class GenerateCampaignIdeaResponse(BaseModel):
    campaign_name: str
    """Name of the campaign being promoted."""

    description: str
    """Detailed description explaining the campaign purpose."""

    strategy: str
    """Suggested strategy to execute the campaign."""


class GenerateMarketingSloganRequest(BaseModel):
    campaign: GenerateCampaignIdeaResponse
    """Full campaign details (name, description, and strategy) used to generate slogans."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "campaign": {
                        "campaign_name": "Focus Asia 20",
                        "description": "A regional campaign to boost monitor sales by highlighting productivity.",
                        "strategy": "Leverage social media influencers and promote bundled deals."
                    }
                }
            ]
        }
    }


class GenerateMarketingSloganResponse(BaseModel):
    slogans: List[str]
    """List of suggested marketing slogans tailored to the campaign."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "slogans": [
                        "Power Up Your Productivity!",
                        "The Monitor That Works As Hard As You Do.",
                        "Boost Your Vision, Boost Your Goals."
                    ]
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
)


@prt.api("/generate-marketing-slogan", spec=api_spec)
async def run(payload: GenerateMarketingSloganRequest, **kwargs) -> GenerateMarketingSloganResponse:
    """
    Generate catchy marketing slogans from a campaign description and strategy.

    Use this tool when a campaign is already defined and you need creative slogan ideas.
    The input must contain a structured campaign object including name, description, and strategy.
    The output is a list of short slogans designed to align with the campaign tone and goal.

    Ideal for marketing teams looking to quickly brainstorm branding lines.
    """

    description = payload.campaign.description.lower()

    if "productivity" in description:
        slogans = [
            "Power Up Your Productivity!",
            "Work Smarter, See Sharper.",
            "Boost Your Workflow with Every Pixel."
        ]
    elif "deal" in description:
        slogans = [
            "Big Value, Bigger Vision.",
            "Bundles That Mean Business.",
            "Smart Tech. Smarter Price."
        ]
    else:
        slogans = [
            "Your Tech, Your Edge.",
            "Be Bold. Be Better.",
            "Innovation in Every Click."
        ]

    return GenerateMarketingSloganResponse(slogans=slogans)

```

### apis/generate_social_posts.py
```python
# apis/generate_social_posts.py
import practicuscore as prt
from pydantic import BaseModel


class GenerateSocialPostsRequest(BaseModel):
    campaign_name: str
    """Name of the campaign to generate social posts for"""

    slogan: str
    """Main slogan that will be used across all posts"""

    target_audience: str
    """Short description of who the campaign is targeting"""

    tone: str
    """Tone of voice to be used such as energetic professional or friendly"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "campaign_name": "Focus Asia 20",
                    "slogan": "Power Up Your Productivity",
                    "target_audience": "Young professionals working remotely in Asia",
                    "tone": "energetic"
                }
            ]
        }
    }


class GenerateSocialPostsResponse(BaseModel):
    linkedin_post: str
    """Generated text post suitable for LinkedIn platform"""

    instagram_caption: str
    """Generated caption designed for Instagram audience"""

    twitter_post: str
    """Generated short post suitable for Twitter or X platform"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "linkedin_post": "Power Up Your Productivity Reach new heights in your remote career with the latest gear",
                    "instagram_caption": "Power meets portability Boost your workflow and elevate your hustle",
                    "twitter_post": "Level up your workspace Power Up Your Productivity"
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=False,
    risk_profile=prt.APIRiskProfile.Medium,
)


@prt.api("/generate-social-posts", spec=api_spec)
async def run(payload: GenerateSocialPostsRequest, **kwargs) -> GenerateSocialPostsResponse:
    """
    Generate platform specific social media posts based on a campaign slogan and audience

    Use this tool after a campaign and slogan are finalized
    Provide the campaign name slogan target audience and tone to receive tailored post texts
    The output includes text formatted for linkedin instagram and twitter
    This tool helps marketing teams save time by creating audience matched content automatically
    """

    slogan = payload.slogan
    audience = payload.target_audience
    tone = payload.tone.lower()

    if "energetic" in tone:
        linkedin = f"{slogan} Reach new heights in your remote career with the latest gear"
        instagram = f"{slogan} Boost your workflow and elevate your hustle"
        twitter = f"Level up your workspace {slogan}"
    elif "professional" in tone:
        linkedin = f"{slogan} A smarter way to work for modern professionals in {audience}"
        instagram = f"{slogan} Designed with professionals in mind"
        twitter = f"{slogan} Professional tools for serious results"
    else:
        linkedin = f"{slogan} Connect with what matters most Perfect for {audience}"
        instagram = f"{slogan} A better day starts with smarter tech"
        twitter = f"{slogan} Ready when you are"

    return GenerateSocialPostsResponse(
        linkedin_post=linkedin,
        instagram_caption=instagram,
        twitter_post=twitter
    )

```

### apis/generate_strategic_summary.py
```python
# apis/generate_strategic_summary.py

import practicuscore as prt
from pydantic import BaseModel


class CampaignIdea(BaseModel):
    campaign_name: str
    """The name of the campaign."""

    description: str
    """A brief explanation of the campaign."""

    strategy: str
    """The strategy to be used in the campaign."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "campaign_name": "Monitor Boost in Asia",
                    "description": "This campaign focuses on growing Monitor sales in Asia, supporting the goal: 'Increase monitor sales in Asia by 20% in Q2.'",
                    "strategy": "Leverage digital ads and local influencers in Asia. Highlight features that align with productivity and affordability."
                }
            ]
        }
    }


class StrategicSummaryResponse(BaseModel):
    summary: str
    """A concise strategic overview of the campaign."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "The campaign targets a high-growth region using localized advertising and product positioning to emphasize productivity gains."
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
)


@prt.api("/generate-strategic-summary", spec=api_spec)
async def run(payload: CampaignIdea, **kwargs) -> StrategicSummaryResponse:
    """
    This tool generates a short strategic summary from a campaign idea
    It is used when a decision maker wants a quick strategic overview of a campaign's purpose and method
    Input includes campaign name, description, and strategy
    Output includes a synthesized sentence summarizing the strategic intent
    Useful for briefings and high-level analysis
    """

    summary = f"The campaign '{payload.campaign_name}' aims to achieve its business goal by {payload.strategy.lower()}. It is designed to address the objective: {payload.description}"
    return StrategicSummaryResponse(summary=summary)

```

### apis/predict_growth_opportunities.py
```python
# apis/predict_growth_opportunities.py
import practicuscore as prt
from pydantic import BaseModel, Field
from typing import List, Literal


class TopProduct(BaseModel):
    product: str
    """Name of the top-performing product"""

    total_units_sold: int
    """Total number of units sold for this product"""

    top_region: str
    """Region where the product sold the most"""


class RegionalDrop(BaseModel):
    region: str
    """Region where sales performance declined"""

    product: str
    """Product that experienced the drop"""

    drop_percentage: float
    """Percentage of decline in sales for this product-region pair"""


class SalesTrendSummary(BaseModel):
    trend_direction: Literal["increasing", "decreasing", "stable"]
    """Overall direction of sales trend"""

    peak_day: str
    """Day with the highest sales, in YYYY-MM-DD format"""


class PredictGrowthOpportunitiesRequest(BaseModel):
    top_products: List[TopProduct] = Field(..., description="List of products with strong recent sales performance")
    regional_drops: List[RegionalDrop] = Field(..., description="List of product-region pairs that showed declining performance")
    trend_summary: SalesTrendSummary = Field(..., description="General sales performance pattern during the period")

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "top_products": [
                        {
                            "product": "Monitor",
                            "total_units_sold": 5000,
                            "top_region": "Europe"
                        },
                        {
                            "product": "Tablet",
                            "total_units_sold": 4200,
                            "top_region": "Asia"
                        }
                    ],
                    "regional_drops": [
                        {
                            "region": "Asia",
                            "product": "Monitor",
                            "drop_percentage": 42.5
                        }
                    ],
                    "trend_summary": {
                        "trend_direction": "increasing",
                        "peak_day": "2025-01-12"
                    }
                }
            ]
        }
    }



class GrowthOpportunity(BaseModel):
    product: str
    """Product recommended for campaign focus"""

    region: str
    """Region recommended for targeting"""

    reason: str
    """Justification for suggesting this product-region pair"""

    confidence: Literal["high", "medium", "low"]
    """Confidence level in this opportunity recommendation"""


class PredictGrowthOpportunitiesResponse(BaseModel):
    opportunities: List[GrowthOpportunity]
    """List of suggested product-region growth opportunities"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "opportunities": [
                        {
                            "product": "Tablet",
                            "region": "Europe",
                            "reason": "Strong historical performance and overall increasing sales trend.",
                            "confidence": "high"
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
)


@prt.api("/predict-growth-opportunities", spec=api_spec)
async def run(payload: PredictGrowthOpportunitiesRequest, **kwargs) -> PredictGrowthOpportunitiesResponse:
    """
    Identify potential growth opportunities for future campaigns.

    Required input structure:
    - top_products: List of high-performing products. Each item must include:
        * product (str)
        * total_units_sold (int)
        * top_region (str)

    - regional_drops: List of regions where sales dropped. Each item must include:
        * region (str)
        * product (str)
        * drop_percentage (float)

    - trend_summary: Required object that describes overall sales behavior. Must include:
        * trend_direction (str): One of "increasing", "decreasing", "stable"
        * peak_day (str): Format YYYY-MM-DD, e.g. "2025-01-10"

    Warning: If trend_summary is missing, this API will fail. 
    Make sure to call a sales analysis tool beforehand that provides this summary.
    """

    try:
        if isinstance(payload, dict):
            payload = PredictGrowthOpportunitiesRequest(**payload)
        opportunities = []

        for product in payload.top_products:
            confidence = "medium"
            reason_parts = []

            if payload.trend_summary.trend_direction == "increasing":
                reason_parts.append("Overall sales trend is increasing.")
                confidence = "high"

            if any(d.product == product.product and d.region == product.top_region for d in payload.regional_drops):
                reason_parts.append(f"But note there was a recent drop in {product.top_region}")
                confidence = "medium" if confidence == "high" else "low"

            reason = " ".join(reason_parts) or "Stable performance with consistent results."

            opportunities.append(GrowthOpportunity(
                product=product.product,
                region=product.top_region,
                reason=reason,
                confidence=confidence
            ))

        return PredictGrowthOpportunitiesResponse(opportunities=opportunities)

    except Exception as e:
        prt.logger.error(f"[predict-growth-opportunities] Exception: {e}")
        raise

```

### apis/sentiment_test_slogan.py
```python
# apis/sentiment_test_slogan.py
import practicuscore as prt
from pydantic import BaseModel
from typing import List, Literal
from langchain_openai import ChatOpenAI


class SentimentTestSloganRequest(BaseModel):
    slogans: List[str]
    """List of slogans to analyze for emotional sentiment"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [{
                "slogans": [
                    "Power Up Your Productivity!",
                    "You Deserve Better."
                ]
            }]
        }
    }


class SloganSentimentResult(BaseModel):
    slogan: str
    """The original marketing slogan"""

    sentiment: Literal["positive", "neutral", "negative"]
    """Detected emotional sentiment of the slogan"""

    comment: str
    """Short explanation of the sentiment classification"""


class SentimentTestSloganResponse(BaseModel):
    results: List[SloganSentimentResult]
    """Sentiment results for each input slogan"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [{
                "results": [
                    {
                        "slogan": "Power Up Your Productivity!",
                        "sentiment": "positive",
                        "comment": "This slogan conveys a sense of motivation and improvement."
                    },
                    {
                        "slogan": "You Deserve Better.",
                        "sentiment": "neutral",
                        "comment": "This slogan implies improvement but lacks strong emotional cues."
                    }
                ]
            }]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
)


@prt.api("/sentiment-test-slogan", spec=api_spec)
async def run(payload: SentimentTestSloganRequest, **kwargs) -> SentimentTestSloganResponse:
    """
    Analyze the emotional sentiment of given marketing slogans using a language model

    Use this tool when you have one or more slogans and want to understand the
    emotional tone behind each one. The output helps determine if a slogan
    is likely to be received as positive, neutral, or negative.

    Useful for validating slogans before launching marketing campaigns.
    """

    openaikey, age = prt.vault.get_secret("openaikey")
    api_key = openaikey

    llm = ChatOpenAI(api_key=api_key, model="gpt-4o", temperature=0.3, streaming=False)

    slogans_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(payload.slogans)])
    prompt = f"""
You are a sentiment analysis assistant.

Evaluate the emotional sentiment of each of the following marketing slogans.

For each slogan, return a JSON object with the following fields:
- slogan
- sentiment (one of: positive, neutral, negative)
- comment (short explanation why)

Output a JSON array.

Slogans:
{slogans_text}
"""

    response = llm.invoke(prompt)
    response_text = response.content.strip()

    results = []
    for slogan in payload.slogans:
        slogan_lower = slogan.lower()
        sentiment = "neutral"
        comment = "Could not confidently extract sentiment."

        for line in response_text.splitlines():
            if slogan_lower[:10] in line.lower() or slogan_lower in line.lower():
                if "positive" in line.lower():
                    sentiment = "positive"
                elif "negative" in line.lower():
                    sentiment = "negative"
                elif "neutral" in line.lower():
                    sentiment = "neutral"
                comment = line.strip()
                break

        results.append(SloganSentimentResult(
            slogan=slogan,
            sentiment=sentiment,
            comment=comment
        ))

    return SentimentTestSloganResponse(results=results)

```

### apis/suggest_target_audience.py
```python
# apis/suggest_target_audience.py
import practicuscore as prt
from pydantic import BaseModel
from typing import List


class GenerateCampaignIdeaResponse(BaseModel):
    campaign_name: str
    """Name of the campaign"""

    description: str
    """Detailed explanation of the campaign idea"""

    strategy: str
    """Planned marketing strategy for this campaign"""


class SuggestTargetAudienceRequest(BaseModel):
    campaign: GenerateCampaignIdeaResponse
    """The campaign details for which target audience suggestions will be generated"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "campaign": {
                        "campaign_name": "Focus Asia 20",
                        "description": "Boost monitor sales in Asia by promoting productivity.",
                        "strategy": "Use influencer marketing on tech-focused platforms."
                    }
                }
            ]
        }
    }


class AudienceSegment(BaseModel):
    segment_name: str
    """Name of the audience group"""

    age_range: str
    """Typical age range for the audience"""

    profession: str
    """Common job or professional background"""

    interests: List[str]
    """Main interests of this audience segment"""

    persona_summary: str
    """Concise summary describing the lifestyle or preferences of this group"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "segment_name": "Young Remote Workers",
                    "age_range": "25–34",
                    "profession": "Freelancers, Startup Employees",
                    "interests": ["productivity tools", "tech gear", "remote work"],
                    "persona_summary": "Digitally native professionals who value mobility, speed, and high-performance equipment."
                }
            ]
        }
    }


class SuggestTargetAudienceResponse(BaseModel):
    audience_segments: List[AudienceSegment]
    """Suggested audience groups relevant to the campaign"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "audience_segments": [
                        {
                            "segment_name": "Young Remote Workers",
                            "age_range": "25–34",
                            "profession": "Freelancers, Startup Employees",
                            "interests": ["productivity tools", "tech gear", "remote work"],
                            "persona_summary": "Digitally native professionals who value mobility, speed, and high-performance equipment."
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
)


@prt.api("/suggest-target-audience", spec=api_spec)
async def run(payload: SuggestTargetAudienceRequest, **kwargs) -> SuggestTargetAudienceResponse:
    """
    Suggest audience segments that are most relevant to a given marketing campaign

    Use this tool when you already have a campaign idea and need to find the most appropriate
    audience groups to target. This helps align the campaign's messaging and channels with
    consumer personas that are most likely to respond.

    The input should include the campaign's name, description, and strategy.
    The output includes one or more audience segments with persona details.
    """

    idea = payload.campaign.description.lower()

    if "remote" in idea or "productivity" in idea:
        segments = [
            AudienceSegment(
                segment_name="Young Remote Workers",
                age_range="25–34",
                profession="Freelancers, Startup Employees",
                interests=["productivity tools", "tech gear", "remote work"],
                persona_summary="Digitally native professionals who value mobility, speed, and high-performance equipment."
            )
        ]
    else:
        segments = [
            AudienceSegment(
                segment_name="General Tech Buyers",
                age_range="30–45",
                profession="Corporate Employees",
                interests=["gadgets", "deals", "online shopping"],
                persona_summary="Professionals with moderate tech interest and stable income, responsive to performance-based messaging."
            )
        ]

    return SuggestTargetAudienceResponse(audience_segments=segments)

```

### apis/top_products_insight.py
```python
# apis/top_products_insight.py
import practicuscore as prt
from pydantic import BaseModel
from typing import List
from datetime import datetime


class SalesRecord(BaseModel):
    date: datetime
    """Date of the sales record in ISO format with timezone"""

    product: str
    """Name of the product that was sold"""

    region: str
    """Region where the product sale occurred"""

    units_sold: int
    """Number of units sold in this record"""

    revenue: float
    """Revenue earned from this sale"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "date": "2024-12-01T00:00:00Z",
                    "product": "Tablet",
                    "region": "Europe",
                    "units_sold": 90,
                    "revenue": 36000.0
                }
            ]
        }
    }


class TopProductsInsightRequest(BaseModel):
    sales_data: List[SalesRecord]
    """Complete list of sales data records to analyze"""

    top_n: int
    """Number of top products to return based on units sold"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "sales_data": [
                        {
                            "date": "2024-12-01T00:00:00Z",
                            "product": "Tablet",
                            "region": "Europe",
                            "units_sold": 90,
                            "revenue": 36000.0
                        }
                    ],
                    "top_n": 3
                }
            ]
        }
    }


class ProductInsight(BaseModel):
    product: str
    """The name of the product identified as top selling"""

    total_units_sold: int
    """Total units sold across all regions for this product"""

    top_region: str
    """Region where this product had the most sales"""

    insight: str
    """Comment or hypothesis about why this product performed well"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "product": "Tablet",
                    "total_units_sold": 7250,
                    "top_region": "Europe",
                    "insight": "Popular among mobile professionals for its portability and pricing."
                }
            ]
        }
    }


class TopProductsInsightResponse(BaseModel):
    products: List[ProductInsight]
    """List of insights for top-performing products"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "products": [
                        {
                            "product": "Tablet",
                            "total_units_sold": 7250,
                            "top_region": "Europe",
                            "insight": "Popular among mobile professionals for its portability and pricing."
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
)



@prt.api("/top-products-insight", spec=api_spec)
async def run(payload: TopProductsInsightRequest, **kwargs) -> TopProductsInsightResponse:
    """
    Identify the top performing products based on units sold and revenue.
    Returns a list of products with regional performance insights.
    """
    try:
        

        product_totals = {}
        region_tracker = {}

        for record in payload.sales_data:
            key = record.product
            product_totals.setdefault(key, 0)
            product_totals[key] += record.units_sold

            region_tracker.setdefault(key, {})
            region_tracker[key].setdefault(record.region, 0)
            region_tracker[key][record.region] += record.units_sold

        top = sorted(product_totals.items(), key=lambda x: x[1], reverse=True)
        top_n = top[:payload.top_n]

        results = []
        for product, total_units in top_n:
            top_region = max(region_tracker[product], key=region_tracker[product].get)
            results.append(ProductInsight(
                product=product,
                total_units_sold=total_units,
                top_region=top_region,
                insight=f"{product} performs best in {top_region}, likely due to high demand and competitive pricing."
            ))

        return TopProductsInsightResponse(products=results)

    except Exception as e:
        prt.logger.error(f"[top-products-insight] Exception: {e}")
        raise

```

### apis/validate_campaign_json.py
```python
# apis/validate_campaign_json.py
import practicuscore as prt
from pydantic import BaseModel
from typing import List


class CampaignData(BaseModel):
    campaign_name: str
    """Name of the campaign to be validated"""

    description: str
    """Detailed description of the campaign’s objective and context"""

    strategy: str
    """High-level marketing strategy or approach"""

    slogans: List[str]
    """List of proposed slogans that support the campaign"""

    audience_segments: List[str]
    """Target customer segments the campaign is intended for"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "campaign_name": "Focus Asia 20",
                    "description": "Boost monitor sales in Asia with productivity-focused messaging.",
                    "strategy": "Use influencers on social media platforms and offer bundle promotions.",
                    "slogans": ["Power Up Your Productivity!", "See More, Do More."],
                    "audience_segments": ["Young Remote Workers", "Tech-Savvy Freelancers"]
                }
            ]
        }
    }


class ValidateCampaignJSONResponse(BaseModel):
    is_valid: bool
    """Indicates if the campaign JSON object is structurally complete"""

    missing_fields: List[str]
    """Names of fields that are missing or empty"""

    message: str
    """Explanation message summarizing the validation result"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "is_valid": False,
                    "missing_fields": ["strategy"],
                    "message": "Missing required field(s): strategy."
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low,
)


@prt.api("/validate-campaign-json", spec=api_spec)
async def run(payload: CampaignData, **kwargs) -> ValidateCampaignJSONResponse:
    """
    Validate if a campaign object is complete and ready to be used in downstream tools

    This tool checks the internal structure of a campaign definition to ensure that
    all required fields are present and non-empty.

    Use this tool when:
    - You receive a campaign JSON from another tool or agent
    - You want to ensure no critical data (like name, strategy, or slogans) is missing
    - You want to fail-fast before further processing a campaign

    Input: Campaign object with fields like name, description, strategy, slogans, and audience
    Output: A boolean indicating if the campaign is valid and which fields are missing if any
    """

    missing = []

    if not payload.campaign_name.strip():
        missing.append("campaign_name")
    if not payload.description.strip():
        missing.append("description")
    if not payload.strategy.strip():
        missing.append("strategy")
    if not payload.slogans or all(not s.strip() for s in payload.slogans):
        missing.append("slogans")
    if not payload.audience_segments:
        missing.append("audience_segments")

    is_valid = len(missing) == 0
    message = "All required fields are present." if is_valid else f"Missing required field(s): {', '.join(missing)}."

    return ValidateCampaignJSONResponse(
        is_valid=is_valid,
        missing_fields=missing,
        message=message
    )

```


---

**Previous**: [Lang Chain LLM Model](../../advanced-langchain/lang-chain-llm-model.md) | **Next**: [Hr > Build](../hr/build.md)
