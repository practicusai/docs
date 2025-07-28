# apis/analyze_complaint_topics.py

import practicuscore as prt
from pydantic import BaseModel
from typing import List, Dict
from collections import Counter
import re


class Complaint(BaseModel):
    customer_id: str
    """Customer's unique identifier."""

    complaint_text: str
    """Free-form text describing a customer's complaint."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {"customer_id": "C001", "complaint_text": "Service was too slow and no one responded to my emails."},
                {"customer_id": "C002", "complaint_text": "Billing is incorrect for the last two months!"}
            ]
        }
    }


class ComplaintTopic(BaseModel):
    topic: str
    """Identified complaint topic keyword or phrase."""

    count: int
    """Number of times the topic was detected."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [{"topic": "billing", "count": 5}, {"topic": "support", "count": 3}]
        }
    }


class AnalyzeComplaintTopicsRequest(BaseModel):
    complaints: List[Complaint]
    """List of raw customer complaints."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "complaints": [
                        {"customer_id": "C001", "complaint_text": "Your mobile app keeps crashing."},
                        {"customer_id": "C002", "complaint_text": "The delivery was delayed twice."}
                    ]
                }
            ]
        }
    }


class AnalyzeComplaintTopicsResponse(BaseModel):
    topics: List[ComplaintTopic]
    """Most frequent complaint topics extracted from the text corpus."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": {
                "topics": [
                    {"topic": "app crash", "count": 4},
                    {"topic": "delivery delay", "count": 3}
                ]
            }
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Low
)


@prt.api("/analyze-complaint-topics", spec=api_spec)
async def run(payload: AnalyzeComplaintTopicsRequest, **kwargs) -> AnalyzeComplaintTopicsResponse:
    """
    Extracts the most common complaint topics from free-text customer complaints.
    """

    topic_keywords = ["billing", "delivery", "support", "login", "app", "refund", "delay", "payment", "email", "cancel"]
    topic_counter = Counter()

    for complaint in payload.complaints:
        text = complaint.complaint_text.lower()
        for keyword in topic_keywords:
            if re.search(rf"\b{re.escape(keyword)}\b", text):
                topic_counter[keyword] += 1

    topics = [ComplaintTopic(topic=k, count=v) for k, v in topic_counter.most_common()]

    return AnalyzeComplaintTopicsResponse(topics=topics)
