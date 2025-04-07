from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class Tenant(BaseModel):
    tenant_index: int
    product_id: str
    bill_details: Optional[Dict[str, Any]] = None


class TenantsRequest(BaseModel):
    tenants: List[Tenant]


class TenantsResponse(BaseModel):
    tenants: List[Tenant]