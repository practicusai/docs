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
app_name = "agentic-ai-test-hr"
visible_name = "Agentic AI Test HR"
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
    "load-hr-data/",
    "detect-behavior-flags/",
    "detect-burnout-risk/",
    "evaluate-promotion-readiness/",
    "generate-manager-insights/",
    "summarize-team-status/",
    "generate-growth-goals/",
    "simulate-policy-impact/",
    "generate-org-wide-summary/",
    "detect-attrition-risk/",
    "analyze-engagement-trend/",
    "calculate-team-resilience/",
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

## queries
"
I would like a general analysis of team performance over the past 6 months. Which teams have shown higher performance and which ones had higher absence rates? Also, could you provide a brief summary of overall workforce stability?"

"Can you provide a comparative analysis of productivity and absence patterns across departments over the last quarter? I'm especially interested in identifying departments with consistently high performance and those with frequent absences."

```python
query = """
As part of our ongoing workforce analytics initiative, I’m interested in understanding how performance and attendance trends have evolved across departments over the past half year. Which teams demonstrate consistent productivity, and which ones show signs of fluctuation? Additionally, I would appreciate a high-level summary outlining overall organizational health, including patterns in feedback quality and team cohesion metrics if available.

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


sales_data = [
    SalesRecord(date=datetime(2025, 1, 1), product="Laptop", region="Asia", units_sold=120, revenue=120000.0),
    SalesRecord(date=datetime(2025, 1, 2), product="Laptop", region="Asia", units_sold=100, revenue=100000.0),
    SalesRecord(date=datetime(2025, 1, 3), product="Tablet", region="Europe", units_sold=80, revenue=32000.0),
    SalesRecord(date=datetime(2025, 1, 4), product="Tablet", region="Europe", units_sold=70, revenue=28000.0),
    SalesRecord(date=datetime(2025, 1, 5), product="Monitor", region="North America", units_sold=95, revenue=47500.0),
]


payload = TopProductsInsightRequest(sales_data=sales_data, top_n=3)


try:
    response: TopProductsInsightResponse = prt.apps.test_api("/top-products-insight", payload)

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

### apis/analyze_engagement_trend.py
```python
# apis/analyze_engagement_trend.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List


class HRRecord(BaseModel):
    employee_id: str
    """Unique identifier for the employee."""

    date: str
    """Timestamp of the HR record."""

    performance_score: float
    """Performance score at that time."""

    absence_days: float
    """Number of absence days within the period."""

    feedback_text: str
    """Free-form feedback or comment received."""


class EngagementTrend(BaseModel):
    employee_id: str
    """Employee for whom the trend is analyzed."""

    trend_direction: str
    """Direction of engagement trend: 'Improving', 'Declining', or 'Stable'."""

    insight: str
    """LLM-generated explanation of why this trend was detected."""

    intervention_needed: bool
    """Whether action should be taken based on this trend."""


class AnalyzeEngagementTrendRequest(BaseModel):
    records: List[HRRecord]
    """Historical HR records used to detect engagement trend."""


class AnalyzeEngagementTrendResponse(BaseModel):
    trends: List[EngagementTrend]
    """Trend evaluations per employee."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True,
)


@prt.api("/analyze-engagement-trend", spec=api_spec)
async def run(payload: AnalyzeEngagementTrendRequest, **kwargs) -> AnalyzeEngagementTrendResponse:
    """
    Analyzes historical engagement signals to detect trends in employee behavior over time,
    highlighting if intervention may be required.
    """
    dummy = EngagementTrend(
        employee_id=payload.records[0].employee_id,
        trend_direction="Declining",
        insight="Performance scores are dropping steadily while absenteeism is increasing. Feedback mentions loss of motivation.",
        intervention_needed=True
    )

    return AnalyzeEngagementTrendResponse(trends=[dummy])

```

### apis/calculate_team_resilience.py
```python
# apis/calculate_team_resilience.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List


class TeamBehaviorSignal(BaseModel):
    employee_id: str
    """The ID of the employee."""

    team: str
    """Team name the employee belongs to."""

    signal: str
    """Short label of behavioral pattern."""

    rationale: str
    """Explanation of the signal."""


class TeamResilienceScore(BaseModel):
    team: str
    """Team name."""

    resilience_level: str
    """Estimated resilience level: High, Medium, Low."""

    explanation: str
    """Explanation of the score assigned."""

    improvement_advice: str
    """Suggested interventions to improve resilience."""


class CalculateTeamResilienceRequest(BaseModel):
    signals: List[TeamBehaviorSignal]
    """Team-wide behavioral signals."""


class CalculateTeamResilienceResponse(BaseModel):
    scores: List[TeamResilienceScore]
    """Resilience scores per team."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True,
)


@prt.api("/calculate-team-resilience", spec=api_spec)
async def run(payload: CalculateTeamResilienceRequest, **kwargs) -> CalculateTeamResilienceResponse:
    """
    Evaluates the resilience level of teams based on behavioral patterns, providing strategic guidance
    on how to strengthen adaptability and cohesion during stress or change.
    """
    dummy = TeamResilienceScore(
        team=payload.signals[0].team,
        resilience_level="Medium",
        explanation="Team shows moderate fluctuation under pressure. Some members display warning signs during tight deadlines.",
        improvement_advice="Introduce stress-coping workshops and team retrospectives to improve trust and adaptability."
    )

    return CalculateTeamResilienceResponse(scores=[dummy])

```

### apis/detect_attrition_risk.py
```python
# apis/detect_attrition_risk.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List


class BehaviorSignal(BaseModel):
    employee_id: str
    """The employee to whom this behavioral signal applies."""

    signal: str
    """Short label of detected behavioral trend."""

    rationale: str
    """Explanation of why this signal was detected."""


class AttritionRisk(BaseModel):
    employee_id: str
    """ID of the employee being evaluated for attrition risk."""

    risk_level: str
    """Predicted risk level of voluntary attrition: High, Medium, Low, or None."""

    justification: str
    """LLM-generated explanation for the assigned risk level."""


class DetectAttritionRiskRequest(BaseModel):
    signals: List[BehaviorSignal]
    """Behavioral signals used to assess attrition likelihood."""


class DetectAttritionRiskResponse(BaseModel):
    risks: List[AttritionRisk]
    """Attrition risk evaluations for each employee."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True,
)


@prt.api("/detect-attrition-risk", spec=api_spec)
async def run(payload: DetectAttritionRiskRequest, **kwargs) -> DetectAttritionRiskResponse:
    """
    Predicts the likelihood of employee attrition based on behavioral patterns,
    providing risk levels and reasoning to help prevent unexpected turnover.
    """
    dummy = AttritionRisk(
        employee_id=payload.signals[0].employee_id,
        risk_level="High",
        justification="Employee has shown signs of disengagement, missed growth expectations, and high absenteeism."
    )

    return DetectAttritionRiskResponse(risks=[dummy])

```

### apis/detect_behavior_flags.py
```python
# apis/detect_behavior_flags.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List, Optional


class HRRecord(BaseModel):
    employee_id: str
    """Employee identifier."""

    date: str
    """Record date (format: YYYY-MM-DD)."""

    performance_score: Optional[float]
    """Score representing employee's performance."""

    absence_days: Optional[float]
    """Number of days the employee was absent."""

    feedback_text: Optional[str]
    """Feedback comment or remark."""

    team: Optional[str]
    """Team name; if not provided, will be defaulted."""


class BehaviorFlag(BaseModel):
    employee_id: str
    """Employee for whom the flag was detected."""

    absence_flag: bool
    """True if absence_days > 5."""

    performance_flag: bool
    """True if performance_score < 2.5."""

    team: str
    """Normalized team name for grouping."""


class DetectBehaviorFlagsRequest(BaseModel):
    records: List[HRRecord]
    """List of HR records to evaluate."""


class DetectBehaviorFlagsResponse(BaseModel):
    flags: List[BehaviorFlag]
    """Flags for each employee indicating behavioral signals."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low,
    interactive=True,
)


@prt.api("/detect-behavior-flags", spec=api_spec)
async def run(payload: DetectBehaviorFlagsRequest) -> DetectBehaviorFlagsResponse:
    """Detect simple behavioral flags like high absence or low performance."""
    flags = []

    for r in payload.records:
        absence_flag = (r.absence_days or 0) > 5
        performance_flag = (r.performance_score or 5) < 2.5
        team = r.team if r.team else "Unknown"

        flags.append(BehaviorFlag(
            employee_id=r.employee_id,
            absence_flag=absence_flag,
            performance_flag=performance_flag,
            team=team
        ))

    return DetectBehaviorFlagsResponse(flags=flags)

```

### apis/detect_burnout_risk.py
```python
# apis/detect_burnout_risk.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List


class BehaviorSignal(BaseModel):
    employee_id: str
    """The employee to whom this behavioral signal applies."""

    signal: str
    """Short label describing the type of behavioral signal (e.g. 'Burnout Risk')."""

    rationale: str
    """Explanation of why this signal was detected based on behavioral history."""


class BurnoutRisk(BaseModel):
    employee_id: str
    """Unique identifier for the employee."""

    risk_level: str
    """Risk category (e.g. 'High', 'Medium', 'Low', 'None')."""

    justification: str
    """LLM-generated justification for the burnout risk classification."""


class DetectBurnoutRiskRequest(BaseModel):
    signals: List[BehaviorSignal]
    """List of extracted behavioral signals for each employee."""


class DetectBurnoutRiskResponse(BaseModel):
    risks: List[BurnoutRisk]
    """Burnout risk levels determined for employees, with explanations."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True,
)


@prt.api("/detect-burnout-risk", spec=api_spec)
async def run(payload: DetectBurnoutRiskRequest, **kwargs) -> DetectBurnoutRiskResponse:
    """
    Analyzes behavioral signals using LLM reasoning to identify employees at potential risk of burnout,
    categorizing them as High, Medium, Low, or None with proper justification.
    """
    # Dummy dönüş (gerçek risk analizi zincirde yapılacak)
    dummy_risk = BurnoutRisk(
        employee_id=payload.signals[0].employee_id,
        risk_level="High",
        justification="Combination of negative feedback, fluctuating performance and repeated absences."
    )

    return DetectBurnoutRiskResponse(risks=[dummy_risk])

```

### apis/evaluate_promotion_readiness.py
```python
# apis/evaluate_promotion_readiness.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List


class BehaviorSignal(BaseModel):
    employee_id: str
    """The employee to whom this behavioral signal applies."""

    signal: str
    """Short label describing the type of behavioral signal (e.g. 'Consistent Performer')."""

    rationale: str
    """Explanation of why this signal was detected based on behavioral history."""


class PromotionAssessment(BaseModel):
    employee_id: str
    """Unique identifier for the employee."""

    readiness_level: str
    """Promotion readiness label (e.g. 'Ready', 'Needs Development', 'Not Ready')."""

    justification: str
    """LLM-generated justification explaining why the employee was classified at this level."""


class EvaluatePromotionReadinessRequest(BaseModel):
    signals: List[BehaviorSignal]
    """List of behavioral signals derived from previous analysis."""


class EvaluatePromotionReadinessResponse(BaseModel):
    promotion_recommendations: List[PromotionAssessment]
    """List of promotion readiness levels with justifications."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True,
)


@prt.api("/evaluate-promotion-readiness", spec=api_spec)
async def run(payload: EvaluatePromotionReadinessRequest, **kwargs) -> EvaluatePromotionReadinessResponse:
    """
    Evaluates employees' readiness for promotion based on detected behavioral signals,
    and provides a recommendation with reasoning.
    """
    dummy_assessment = PromotionAssessment(
        employee_id=payload.signals[0].employee_id,
        readiness_level="Ready",
        justification="Employee has shown consistent performance, strong communication, and proactive leadership."
    )

    return EvaluatePromotionReadinessResponse(
        promotion_recommendations=[dummy_assessment]
    )

```

### apis/generate_growth_goals.py
```python
# apis/generate_growth_goals.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List


class BehaviorSignal(BaseModel):
    employee_id: str
    """The employee to whom this behavioral signal applies."""

    signal: str
    """Short label describing the detected behavioral pattern."""

    rationale: str
    """Explanation of why this signal was identified."""


class GrowthGoal(BaseModel):
    employee_id: str
    """The employee for whom the growth goal is generated."""

    goal_title: str
    """Short and actionable growth objective (e.g., 'Improve Time Management')."""

    goal_reasoning: str
    """Explanation of why this specific growth goal was chosen."""

    followup_tip: str
    """Practical suggestion for monitoring or encouraging this goal."""


class GenerateGrowthGoalsRequest(BaseModel):
    signals: List[BehaviorSignal]
    """List of behavior signals to analyze for goal generation."""


class GenerateGrowthGoalsResponse(BaseModel):
    goals: List[GrowthGoal]
    """Generated growth goals for each employee with reasoning."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True,
)


@prt.api("/generate-growth-goals", spec=api_spec)
async def run(payload: GenerateGrowthGoalsRequest, **kwargs) -> GenerateGrowthGoalsResponse:
    """
    Uses behavioral insights to generate personalized growth goals for employees,
    helping managers support their development with clear objectives and follow-ups.
    """
    dummy = GrowthGoal(
        employee_id=payload.signals[0].employee_id,
        goal_title="Improve Time Management",
        goal_reasoning="The employee showed signs of deadline stress and inconsistent task delivery.",
        followup_tip="Suggest weekly check-ins and a self-planned task board."
    )

    return GenerateGrowthGoalsResponse(goals=[dummy])

```

### apis/generate_manager_insights.py
```python
# apis/generate_manager_insights.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List


class BehaviorSignal(BaseModel):
    employee_id: str
    """The employee to whom this behavioral signal applies."""

    signal: str
    """Short label describing the type of behavioral signal."""

    rationale: str
    """Explanation of why this signal was detected."""


class BurnoutRisk(BaseModel):
    employee_id: str
    """Unique identifier for the employee."""

    risk_level: str
    """Burnout risk label (e.g. 'High', 'Medium', 'Low', 'None')."""

    justification: str
    """Justification for the assigned risk level."""


class ManagerInsight(BaseModel):
    employee_id: str
    """The employee for whom the insight is generated."""

    summary: str
    """A brief summary of the employee's current behavioral and risk profile."""

    advice: str
    """Suggested action or communication approach for the manager."""

    development_hint: str
    """Optional development recommendation tailored to the employee."""


class GenerateManagerInsightsRequest(BaseModel):
    signals: List[BehaviorSignal]
    """List of behavioral signals for each employee."""

    risks: List[BurnoutRisk]
    """List of burnout risk assessments."""


class GenerateManagerInsightsResponse(BaseModel):
    insights: List[ManagerInsight]
    """Personalized insight reports per employee for the manager."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True,
)


@prt.api("/generate-manager-insights", spec=api_spec)
async def run(payload: GenerateManagerInsightsRequest, **kwargs) -> GenerateManagerInsightsResponse:
    """
    Generates personalized and actionable insights for managers based on behavioral signals and burnout risks,
    helping them guide, coach, or support each employee effectively.
    """
    dummy = ManagerInsight(
        employee_id=payload.signals[0].employee_id,
        summary="Employee shows signs of fatigue and inconsistency.",
        advice="Schedule a 1-on-1 to discuss workload and recent challenges. Maintain a supportive tone.",
        development_hint="Consider offering time management coaching or mentoring."
    )

    return GenerateManagerInsightsResponse(insights=[dummy])

```

### apis/generate_org_wide_summary.py
```python
# apis/generate_org_wide_summary.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List


class TeamSummary(BaseModel):
    team_name: str
    """Name of the team."""

    health_summary: str
    """Brief summary of team-level observations."""

    risk_distribution: str
    """Burnout risk breakdown."""

    key_recommendation: str
    """Team-level managerial suggestion."""


class OrgWideInsight(BaseModel):
    executive_summary: str
    """One-paragraph strategic summary of the entire workforce health and trends."""

    common_risks: List[str]
    """List of shared concerns across multiple departments."""

    org_opportunities: List[str]
    """Emerging strengths or organizational leverage points."""

    strategic_recommendation: str
    """High-level leadership recommendation (e.g. cultural shift, structure, resourcing)."""


class GenerateOrgWideSummaryRequest(BaseModel):
    team_summaries: List[TeamSummary]
    """Aggregated team summaries to be used for org-wide analysis."""


class GenerateOrgWideSummaryResponse(BaseModel):
    org_summary: OrgWideInsight
    """Strategic summary and insight generation for executive review."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True,
)


@prt.api("/generate-org-wide-summary", spec=api_spec)
async def run(payload: GenerateOrgWideSummaryRequest, **kwargs) -> GenerateOrgWideSummaryResponse:
    """
    Generates a high-level strategic summary across all teams,
    identifying cross-cutting risks, opportunities, and recommendations for leadership.
    """
    dummy = OrgWideInsight(
        executive_summary="Across all departments, there is a growing risk of burnout and disengagement in mid-level roles, while technical teams show resilience.",
        common_risks=["Mid-level manager fatigue", "Disconnect between hybrid teams", "Unclear career paths"],
        org_opportunities=["Strong peer mentoring culture in R&D", "Improved onboarding process in Sales"],
        strategic_recommendation="Initiate leadership upskilling, review role clarity in mid-management, and expand peer mentoring across units."
    )

    return GenerateOrgWideSummaryResponse(org_summary=dummy)

```

### apis/load_hr_data.py.py
```python
# apis/load_hr_data.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import os



class HRRecord(BaseModel):
    employee_id: str
    """Unique identifier for the employee."""

    date: str
    """Date of the HR record (format: YYYY-MM-DD)."""

    performance_score: Optional[float] = None
    """Performance score assigned to the employee."""

    absence_days: Optional[float] = None
    """Number of absence days recorded."""

    feedback_text: Optional[str] = None
    """Free-text feedback or comment regarding the employee."""

    team: Optional[str] = None
    """Team or department the employee belongs to."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "employee_id": "E123",
                    "date": "2024-09-01",
                    "performance_score": 4.2,
                    "absence_days": 1.0,
                    "feedback_text": "Completed tasks consistently, strong communication.",
                    "team": "Marketing"
                }
            ]
        },
    }



class LoadHRDataResponse(BaseModel):
    records: List[HRRecord]
    """List of HR records extracted from the source CSV file."""

    total_employees: int
    """Number of unique employees found in the data."""

    total_records: int
    """Total number of HR records loaded from the file."""

    teams_detected: List[str]
    """List of unique team names identified in the data."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "records": [
                        {
                            "employee_id": "E123",
                            "date": "2024-09-01",
                            "performance_score": 4.2,
                            "absence_days": 1.0,
                            "feedback_text": "Completed tasks consistently, strong communication.",
                            "team": "Marketing"
                        }
                    ],
                    "total_employees": 1,
                    "total_records": 1,
                    "teams_detected": ["Marketing"]
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


@prt.api("/load-hr-data", spec=api_spec)
async def run(**kwargs) -> LoadHRDataResponse:
    """Load historical HR data from a fixed CSV path and return normalized HR records for further analysis."""
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../hr_dataset.csv"))
    df = pd.read_csv(file_path)

    df["team"] = df.get("team", pd.Series(["Unknown"] * len(df)))

    records = [
        HRRecord(
            employee_id=row.get("employee_id", f"UNKNOWN_{i}"),
            date=row.get("date", "1970-01-01"),
            performance_score=row.get("performance_score", None),
            absence_days=row.get("absence_days", 0.0),
            feedback_text=row.get("feedback_text", ""),
            team=row["team"] if isinstance(row, dict) and "team" in row and row["team"] else "Unknown"

        )
        for i, row in df.iterrows()
    ]


    return LoadHRDataResponse(
        records=records,
        total_employees=df["employee_id"].nunique(),
        total_records=len(df),
        teams_detected=df["team"].dropna().unique().tolist()
    )

```

### apis/normalize-hr-records.py
```python
import practicuscore as prt
from pydantic import BaseModel
from typing import List, Optional



class HRRecord(BaseModel):
    employee_id: str
    """Unique identifier for the employee."""

    date: str
    """Date of the HR record (format: YYYY-MM-DD)."""

    performance_score: Optional[float] = None
    """Performance score assigned to the employee."""

    absence_days: Optional[float] = None
    """Number of absence days recorded."""

    feedback_text: Optional[str] = None
    """Free-text feedback or comment regarding the employee."""

    team: Optional[str] = None
    """Team or department the employee belongs to."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "employee_id": "E123",
                    "date": "2024-09-01",
                    "performance_score": 4.2,
                    "absence_days": 1.0,
                    "feedback_text": "Completed tasks consistently, strong communication.",
                    "team": "Marketing"
                }
            ]
        },
    }


class NormalizeHRRecordsResponse(BaseModel):
    normalized_records: List[HRRecord]
    """List of cleaned and normalized HR records."""

    message: str
    """Message indicating status or transformation result."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "normalized_records": [
                        {
                            "employee_id": "E123",
                            "date": "2024-09-01",
                            "performance_score": 4.2,
                            "absence_days": 1.0,
                            "feedback_text": "Completed tasks consistently, strong communication.",
                            "team": "Marketing"
                        }
                    ],
                    "message": "Normalized 1 HR records."
                }
            ]
        },
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=False,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=False,
)


@prt.api("/normalize-hr-records", spec=api_spec)
async def run(records: List[HRRecord]) -> NormalizeHRRecordsResponse:
    """Normalize raw HR records to ensure all fields are complete and standardized."""

    if not records:
        dummy = HRRecord(
            employee_id="DUMMY",
            date="2024-01-01",
            performance_score=3.0,
            absence_days=0.0,
            feedback_text="Placeholder feedback.",
            team="Unknown"
        )
        return NormalizeHRRecordsResponse(
            normalized_records=[dummy],
            message="Input was empty. Injected dummy HR record for simulation."
        )

    normalized = []
    for rec in records:
        normalized.append(
            HRRecord(
                employee_id=rec.employee_id,
                date=rec.date,
                performance_score=rec.performance_score if rec.performance_score is not None else 0.0,
                absence_days=rec.absence_days if rec.absence_days is not None else 0.0,
                feedback_text=rec.feedback_text or "No feedback provided.",
                team=rec.team or "Unknown"
            )
        )

    return NormalizeHRRecordsResponse(
        normalized_records=normalized,
        message=f"Normalized {len(normalized)} HR records."
    )

```

### apis/simulate_policy_impact.py
```python
# apis/simulate_policy_impact.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List


class BehaviorSignal(BaseModel):
    employee_id: str
    """The employee to whom this behavioral signal applies."""

    signal: str
    """Detected behavioral pattern."""

    rationale: str
    """Explanation of why this signal was identified."""


class PolicyChangeProposal(BaseModel):
    title: str
    """Title of the policy or action proposal."""

    description: str
    """Detailed description of what the change will involve."""


class PolicyImpactAssessment(BaseModel):
    expected_outcome: str
    """Overall prediction of how the team will react to this policy change."""

    risks: List[str]
    """Potential negative consequences or resistance areas."""

    opportunities: List[str]
    """Potential benefits or performance gains."""

    implementation_advice: str
    """Suggestions for how to apply the policy with minimal friction."""


class SimulatePolicyImpactRequest(BaseModel):
    signals: List[BehaviorSignal]
    """Current behavioral signals to contextualize the simulation."""

    proposal: PolicyChangeProposal
    """The proposed change or policy to simulate."""


class SimulatePolicyImpactResponse(BaseModel):
    impact: PolicyImpactAssessment
    """AI-generated forecast of the impact of the proposed change."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True,
)


@prt.api("/simulate-policy-impact", spec=api_spec)
async def run(payload: SimulatePolicyImpactRequest, **kwargs) -> SimulatePolicyImpactResponse:
    """
    Uses behavioral insights and policy context to simulate the likely outcome of a proposed change,
    including risks, opportunities, and advice for successful implementation.
    """
    dummy = PolicyImpactAssessment(
        expected_outcome="The proposed remote work policy is likely to increase satisfaction among developers but may reduce alignment in cross-functional teams.",
        risks=["Possible disconnect between departments", "Reduced informal knowledge sharing"],
        opportunities=["Increased autonomy", "Reduced absenteeism", "Higher retention in tech roles"],
        implementation_advice="Introduce structured check-ins and digital team rituals to compensate for reduced face time."
    )

    return SimulatePolicyImpactResponse(impact=dummy)

```

### apis/summarize_team_status.py
```python
# apis/summarize_team_status.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List


class BehaviorSignal(BaseModel):
    employee_id: str
    """The employee to whom this behavioral signal applies."""

    signal: str
    """Short label describing the detected behavioral signal."""

    rationale: str
    """Explanation of why this signal was identified."""


class BurnoutRisk(BaseModel):
    employee_id: str
    """The employee for whom burnout risk is assessed."""

    risk_level: str
    """Risk level classification such as 'High', 'Medium', 'Low', or 'None'."""

    justification: str
    """Justification for the assigned burnout risk level."""


class TeamSummary(BaseModel):
    team_name: str
    """Name of the team this summary is about."""

    health_summary: str
    """General overview of the team's behavioral state and trends."""

    risk_distribution: str
    """Summary of burnout risk levels across team members (e.g., '3 High, 2 Medium, 4 Low')."""

    key_recommendation: str
    """Most important managerial action recommended for the team."""


class SummarizeTeamStatusRequest(BaseModel):
    signals: List[BehaviorSignal]
    """List of behavioral signals detected for all employees."""

    risks: List[BurnoutRisk]
    """List of burnout risk evaluations for all employees."""


class SummarizeTeamStatusResponse(BaseModel):
    summaries: List[TeamSummary]
    """Team-level summaries containing health insights and risk overviews."""


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
    interactive=True,
)


@prt.api("/summarize-team-status", spec=api_spec)
async def run(payload: SummarizeTeamStatusRequest, **kwargs) -> SummarizeTeamStatusResponse:
    """
    Aggregates behavioral signals and burnout risks across employees to create a concise team-level health summary.
    Provides managers with strategic insights and recommendations for action.
    """
    dummy = TeamSummary(
        team_name="Marketing",
        health_summary="The team shows signs of growing fatigue and inconsistent performance.",
        risk_distribution="2 High, 3 Medium, 1 Low",
        key_recommendation="Redistribute workload, conduct check-ins, and rotate responsibilities to avoid burnout clusters."
    )

    return SummarizeTeamStatusResponse(summaries=[dummy])

```


---

**Previous**: [Build](../retention-strategist/build.md) | **Next**: [Inventroy > Build](../inventroy/build.md)
