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
