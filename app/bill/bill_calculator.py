from datetime import timedelta

import httpx
from fastapi.logger import logger

from app.config import get_current_time
from app.db.firebase import database
from app.electricity.service import ElectricityUsageService


async def calculate_monthly_bills_for_all_products():
    """Calculate bills for all products for the previous month"""
    current_time = get_current_time()

    # Get last month's details
    first_day_current_month = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day_last_month = first_day_current_month - timedelta(days=1)
    last_month = last_day_last_month.strftime("%Y-%m")

    logger.info(f"Calculating bills for {last_month}")

    # Get all product IDs from electricity_usage
    usage_data = database.child("electricity_usage").get() or {}
    product_ids = [pid for pid in usage_data.keys() if pid != "connection_status"]

    for product_id in product_ids:
        try:
            # Calculate total kWh for the month
            total_kwh = ElectricityUsageService.calculate_total_kwh_for_month(product_id, last_month)

            # Calculate bill amount
            bill_amount = ElectricityUsageService.calculate_billing_tiers(total_kwh)

            # Save to electricity_bills node
            bill_data = {
                "kw_value": total_kwh,
                "amount": bill_amount,
                "status": "not_paid",
                "payment_date": None,
                "calculated_at": current_time.isoformat()
            }

            database.child(f"electricity_bills/{product_id}/{last_month}").set(bill_data)

            # Notify external API
            await notify_external_api(product_id, last_month , total_kwh , bill_amount )

            logger.info(f"Bill calculated for product {product_id} for {last_month}")

        except Exception as e:
            logger.error(f"Error calculating bill for product {product_id}: {str(e)}")


async def notify_external_api(product_id: str, month: str , total_kwh: float , bill_amount: float):
    """Notify external API about new bill calculation"""
    url = "https://tenantvolt-5cd875450cc3.herokuapp.com/api/bills/send-notification/"
    payload = {
        "product_id": product_id,
        "month": month,
        "amount": bill_amount,
        "kw_value": total_kwh
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to notify external API about bill for {product_id}: {str(e)}")