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
