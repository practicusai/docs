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
