import practicuscore as prt
from pydantic import BaseModel
from typing import List
import pandas as pd
import os


class CustomerProfile(BaseModel):
    customer_id: str
    """Unique identifier for the customer."""

    age: int
    """Age of the customer."""

    gender: str
    """Gender of the customer."""

    location: str
    """Location or region."""

    total_purchases: int
    """Number of past purchases."""

    average_spend: float
    """Average spend per purchase."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "customer_id": "C001",
                    "age": 29,
                    "gender": "Male",
                    "location": "Istanbul",
                    "total_purchases": 12,
                    "average_spend": 78.5
                }
            ]
        }
    }


class LoadCustomerProfileDataResponse(BaseModel):
    customers: List[CustomerProfile]
    """List of structured customer profile records."""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": {
                "customers": [
                    {
                        "customer_id": "C001",
                        "age": 29,
                        "gender": "Male",
                        "location": "Istanbul",
                        "total_purchases": 12,
                        "average_spend": 78.5
                    }
                ]
            }
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    interactive=True,
    risk_profile=prt.APIRiskProfile.Low
)


@prt.api("/load-customer-profile-data", spec=api_spec)
async def run(**kwargs) -> LoadCustomerProfileDataResponse:
    """
    Loads structured customer profile data from a CSV file located in the parent directory.
    """
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../customer_profiles.csv"))
    df = pd.read_csv(file_path)

    customers = [
        CustomerProfile(
            customer_id=str(row["customer_id"]),
            age=int(row["age"]),
            gender=row["gender"],
            location=row["location"],
            total_purchases=int(row["total_purchases"]),
            average_spend=float(row["average_spend"])
        )
        for _, row in df.iterrows()
    ]

    return LoadCustomerProfileDataResponse(customers=customers)
