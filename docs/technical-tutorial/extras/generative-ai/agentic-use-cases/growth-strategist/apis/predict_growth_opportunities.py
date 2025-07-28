# apis/predict_growth_opportunities.py
import practicuscore as prt
from pydantic import BaseModel, Field
from typing import List, Literal


class TopProduct(BaseModel):
    product: str
    """Name of the top-performing product"""

    total_units_sold: int
    """Total number of units sold for this product"""

    top_region: str
    """Region where the product sold the most"""


class RegionalDrop(BaseModel):
    region: str
    """Region where sales performance declined"""

    product: str
    """Product that experienced the drop"""

    drop_percentage: float
    """Percentage of decline in sales for this product-region pair"""


class SalesTrendSummary(BaseModel):
    trend_direction: Literal["increasing", "decreasing", "stable"]
    """Overall direction of sales trend"""

    peak_day: str
    """Day with the highest sales, in YYYY-MM-DD format"""


class PredictGrowthOpportunitiesRequest(BaseModel):
    top_products: List[TopProduct] = Field(..., description="List of products with strong recent sales performance")
    regional_drops: List[RegionalDrop] = Field(..., description="List of product-region pairs that showed declining performance")
    trend_summary: SalesTrendSummary = Field(..., description="General sales performance pattern during the period")

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "top_products": [
                        {
                            "product": "Monitor",
                            "total_units_sold": 5000,
                            "top_region": "Europe"
                        },
                        {
                            "product": "Tablet",
                            "total_units_sold": 4200,
                            "top_region": "Asia"
                        }
                    ],
                    "regional_drops": [
                        {
                            "region": "Asia",
                            "product": "Monitor",
                            "drop_percentage": 42.5
                        }
                    ],
                    "trend_summary": {
                        "trend_direction": "increasing",
                        "peak_day": "2025-01-12"
                    }
                }
            ]
        }
    }



class GrowthOpportunity(BaseModel):
    product: str
    """Product recommended for campaign focus"""

    region: str
    """Region recommended for targeting"""

    reason: str
    """Justification for suggesting this product-region pair"""

    confidence: Literal["high", "medium", "low"]
    """Confidence level in this opportunity recommendation"""


class PredictGrowthOpportunitiesResponse(BaseModel):
    opportunities: List[GrowthOpportunity]
    """List of suggested product-region growth opportunities"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "opportunities": [
                        {
                            "product": "Tablet",
                            "region": "Europe",
                            "reason": "Strong historical performance and overall increasing sales trend.",
                            "confidence": "high"
                        }
                    ]
                }
            ]
        }
    }


api_spec = prt.APISpec(
    execution_target=prt.APIExecutionTarget.DirectExecution,
    read_only=True,
    risk_profile=prt.APIRiskProfile.Medium,
)


@prt.api("/predict-growth-opportunities", spec=api_spec)
async def run(payload: PredictGrowthOpportunitiesRequest, **kwargs) -> PredictGrowthOpportunitiesResponse:
    """
    Identify potential growth opportunities for future campaigns.

    Required input structure:
    - top_products: List of high-performing products. Each item must include:
        * product (str)
        * total_units_sold (int)
        * top_region (str)

    - regional_drops: List of regions where sales dropped. Each item must include:
        * region (str)
        * product (str)
        * drop_percentage (float)

    - trend_summary: Required object that describes overall sales behavior. Must include:
        * trend_direction (str): One of "increasing", "decreasing", "stable"
        * peak_day (str): Format YYYY-MM-DD, e.g. "2025-01-10"

    Warning: If trend_summary is missing, this API will fail. 
    Make sure to call a sales analysis tool beforehand that provides this summary.
    """

    try:
        if isinstance(payload, dict):
            payload = PredictGrowthOpportunitiesRequest(**payload)
        opportunities = []

        for product in payload.top_products:
            confidence = "medium"
            reason_parts = []

            if payload.trend_summary.trend_direction == "increasing":
                reason_parts.append("Overall sales trend is increasing.")
                confidence = "high"

            if any(d.product == product.product and d.region == product.top_region for d in payload.regional_drops):
                reason_parts.append(f"But note there was a recent drop in {product.top_region}")
                confidence = "medium" if confidence == "high" else "low"

            reason = " ".join(reason_parts) or "Stable performance with consistent results."

            opportunities.append(GrowthOpportunity(
                product=product.product,
                region=product.top_region,
                reason=reason,
                confidence=confidence
            ))

        return PredictGrowthOpportunitiesResponse(opportunities=opportunities)

    except Exception as e:
        prt.logger.error(f"[predict-growth-opportunities] Exception: {e}")
        raise
