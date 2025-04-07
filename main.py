import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.electricity.routes import router as electricity_router
from app.bill.routes import router as bill_router
from app.scheduler import start_scheduler, shutdown_scheduler
from app.config import get_current_time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

# Create FastAPI app
app = FastAPI(
    title="TenantVolt Electricity Usage API",
    description="API for retrieving electricity usage data from Firebase Realtime Database",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(electricity_router, prefix="/electricity", tags=["electricity usage"])
app.include_router(bill_router, prefix="/bill", tags=["electricity bills"])

# Register events for scheduler
@app.on_event("startup")
async def startup_event():
    current_time = get_current_time()
    logging.info(f"Starting application at {current_time}")
    start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    shutdown_scheduler()

# Root endpoint
@app.get("/")
async def root():
    current_time = get_current_time()
    return {
        "message": "Welcome to TenantVolt Electricity API",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "current_time": current_time.isoformat()
    }

# Debug endpoint to check current time
@app.get("/debug/time")
async def debug_time():
    current_time = get_current_time()
    return {
        "current_time": current_time.isoformat(),
        "day": current_time.day,
        "hour": current_time.hour,
        "minute": current_time.minute,
        "is_bill_calculation_time": current_time.day == 1 and current_time.hour == 0 and current_time.minute < 10
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)