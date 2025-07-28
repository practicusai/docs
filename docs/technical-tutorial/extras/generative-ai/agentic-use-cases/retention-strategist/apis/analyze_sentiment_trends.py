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
