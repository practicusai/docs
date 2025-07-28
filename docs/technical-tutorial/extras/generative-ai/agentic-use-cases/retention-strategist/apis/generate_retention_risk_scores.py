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
