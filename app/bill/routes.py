from fastapi import APIRouter, HTTPException
import logging

from app.bill.models import TenantsResponse, TenantsRequest, Tenant
from app.db.firebase import database

router = APIRouter()

@router.post("/latest", response_model=TenantsResponse)
async def get_latest_bill_details(request: TenantsRequest):
    """
    Get the latest bill details for each tenant's product ID by finding
    the most recent month in the electricity_bills/{product_id} directory
    """
    response_tenants = []

    for tenant in request.tenants:
        tenant_data = tenant.dict()
        product_id = tenant.product_id

        try:
            # Get all months available for this product_id
            all_months_data = database.child(f"electricity_bills/{product_id}").get()

            if all_months_data:
                # Convert Firebase data to dictionary
                if hasattr(all_months_data, 'val'):
                    all_months = all_months_data.val()
                else:
                    all_months = all_months_data if isinstance(all_months_data, dict) else {}

                # Find the latest month (highest value when sorted)
                if all_months:
                    latest_month = sorted(all_months.keys(), reverse=True)[0]
                    bill_data = all_months[latest_month]

                    tenant_data["bill_details"] = {
                        "month": latest_month,
                        "amount": bill_data.get("amount", 0),
                        "kw_value": bill_data.get("kw_value", 0),
                        "status": bill_data.get("status", "unknown"),
                        "payment_date": bill_data.get("payment_date", None),
                        "calculated_at": bill_data.get("calculated_at", None)
                    }
                else:
                    # No months available
                    tenant_data["bill_details"] = {
                        "month": None,
                        "amount": 0,
                        "kw_value": 0,
                        "status": "no_bill",
                        "payment_date": None,
                        "calculated_at": None
                    }
            else:
                # No bill data at all
                tenant_data["bill_details"] = {
                    "month": None,
                    "amount": 0,
                    "kw_value": 0,
                    "status": "no_bill",
                    "payment_date": None,
                    "calculated_at": None
                }

            response_tenants.append(Tenant(**tenant_data))

        except Exception as e:
            logging.error(f"Error retrieving bill data for product {product_id}: {str(e)}")
            tenant_data["bill_details"] = {
                "error": str(e),
                "status": "error"
            }
            response_tenants.append(Tenant(**tenant_data))

    return TenantsResponse(tenants=response_tenants)