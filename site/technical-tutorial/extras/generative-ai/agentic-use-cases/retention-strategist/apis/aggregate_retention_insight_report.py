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
