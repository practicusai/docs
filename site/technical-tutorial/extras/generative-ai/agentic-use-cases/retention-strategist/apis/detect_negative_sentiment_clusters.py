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
