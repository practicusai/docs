# apis/top_products_insight.py
import practicuscore as prt
from pydantic import BaseModel
from typing import List
from datetime import datetime


class SalesRecord(BaseModel):
    date: datetime
    """Date of the sales record in ISO format with timezone"""

    product: str
    """Name of the product that was sold"""

    region: str
    """Region where the product sale occurred"""

    units_sold: int
    """Number of units sold in this record"""

    revenue: float
    """Revenue earned from this sale"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "date": "2024-12-01T00:00:00Z",
                    "product": "Tablet",
                    "region": "Europe",
                    "units_sold": 90,
                    "revenue": 36000.0
                }
            ]
        }
    }


class TopProductsInsightRequest(BaseModel):
    sales_data: List[SalesRecord]
    """Complete list of sales data records to analyze"""

    top_n: int
    """Number of top products to return based on units sold"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "sales_data": [
                        {
                            "date": "2024-12-01T00:00:00Z",
                            "product": "Tablet",
                            "region": "Europe",
                            "units_sold": 90,
                            "revenue": 36000.0
                        }
                    ],
                    "top_n": 3
                }
            ]
        }
    }


class ProductInsight(BaseModel):
    product: str
    """The name of the product identified as top selling"""

    total_units_sold: int
    """Total units sold across all regions for this product"""

    top_region: str
    """Region where this product had the most sales"""

    insight: str
    """Comment or hypothesis about why this product performed well"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "product": "Tablet",
                    "total_units_sold": 7250,
                    "top_region": "Europe",
                    "insight": "Popular among mobile professionals for its portability and pricing."
                }
            ]
        }
    }


class TopProductsInsightResponse(BaseModel):
    products: List[ProductInsight]
    """List of insights for top-performing products"""

    model_config = {
        "use_attribute_docstrings": True,
        "json_schema_extra": {
            "examples": [
                {
                    "products": [
                        {
                            "product": "Tablet",
                            "total_units_sold": 7250,
                            "top_region": "Europe",
                            "insight": "Popular among mobile professionals for its portability and pricing."
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



@prt.api("/top-products-insight", spec=api_spec)
async def run(payload: TopProductsInsightRequest, **kwargs) -> TopProductsInsightResponse:
    """
    Identify the top performing products based on units sold and revenue.
    Returns a list of products with regional performance insights.
    """
    try:
        

        product_totals = {}
        region_tracker = {}

        for record in payload.sales_data:
            key = record.product
            product_totals.setdefault(key, 0)
            product_totals[key] += record.units_sold

            region_tracker.setdefault(key, {})
            region_tracker[key].setdefault(record.region, 0)
            region_tracker[key][record.region] += record.units_sold

        top = sorted(product_totals.items(), key=lambda x: x[1], reverse=True)
        top_n = top[:payload.top_n]

        results = []
        for product, total_units in top_n:
            top_region = max(region_tracker[product], key=region_tracker[product].get)
            results.append(ProductInsight(
                product=product,
                total_units_sold=total_units,
                top_region=top_region,
                insight=f"{product} performs best in {top_region}, likely due to high demand and competitive pricing."
            ))

        return TopProductsInsightResponse(products=results)

    except Exception as e:
        prt.logger.error(f"[top-products-insight] Exception: {e}")
        raise
