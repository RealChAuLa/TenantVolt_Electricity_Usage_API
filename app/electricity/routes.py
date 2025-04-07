from fastapi import APIRouter, HTTPException

from app.electricity.models import ( ChartDataResponse, ConnectionStatusUpdate, TenantsStatusResponse, TenantsListRequest)
from app.electricity.service import ElectricityUsageService, ConnectionService

router = APIRouter()


@router.get("/minutely/{product_id}/{date}/{hour}", response_model=ChartDataResponse)
async def get_minutely_usage_get(product_id: str, date: str, hour: str):
    """
    Get minute-by-minute electricity usage for a specific hour in a day using GET.

    - product_id: The product identifier
    - date: Date in YYYY-MM-DD format
    - hour: Hour in HH format (00-23)

    Returns data for chart where:
    - X-axis shows minutes (00-59)
    - Y-axis shows average watt values

    This endpoint is publicly accessible.
    """
    return ElectricityUsageService.get_minutely_usage(product_id, date, hour)


@router.get("/hourly/{product_id}/{date}", response_model=ChartDataResponse)
async def get_hourly_usage_get(product_id: str, date: str):
    """
    Get hourly electricity usage for a specific day using GET.

    - product_id: The product identifier
    - date: Date in YYYY-MM-DD format

    Returns data for chart where:
    - X-axis shows hours (00-23)
    - Y-axis shows average watt values

    This endpoint is publicly accessible.
    """
    return ElectricityUsageService.get_hourly_usage(product_id, date)


@router.get("/daily/{product_id}/{year_month}", response_model=ChartDataResponse)
async def get_daily_usage_get(product_id: str, year_month: str):
    """
    Get daily electricity usage for a specific month using GET.

    - product_id: The product identifier
    - year_month: Year and month in YYYY-MM format

    Returns data for chart where:
    - X-axis shows days (01-31)
    - Y-axis shows average watt values

    This endpoint is publicly accessible.
    """
    return ElectricityUsageService.get_daily_usage(product_id, year_month)


@router.get("/monthly/{product_id}/{year}", response_model=ChartDataResponse)
async def get_monthly_usage_get(product_id: str, year: str):
    """
    Get monthly electricity usage for a specific year using GET.

    - product_id: The product identifier
    - year: Year in YYYY format

    Returns data for chart where:
    - X-axis shows months (01-12)
    - Y-axis shows average watt values

    This endpoint is publicly accessible.
    """
    return ElectricityUsageService.get_monthly_usage(product_id, year)


@router.post("/connection-status", response_model=TenantsStatusResponse)
async def get_connection_status(request: TenantsListRequest):
    """
    Get the connection status for each product ID in the request
    """
    tenant_statuses = await ConnectionService.get_connection_statuses(request.tenants)
    return TenantsStatusResponse(tenants=tenant_statuses)


@router.post("/update-connection-status")
async def update_connection_status(request: ConnectionStatusUpdate):
    """
    Update the connection status for a specific product ID
    """
    success = await ConnectionService.update_connection_status(
        request.product_id,
        request.connection_status
    )

    if not success:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update connection status for product {request.product_id}"
        )

    return {
        "message": f"Connection Status of {request.product_id} updated to {request.connection_status} successfully"
    }