import os

from fastapi import FastAPI
from app.electricity.routes import router as electricity_router

# Create FastAPI app
app = FastAPI(
    title="TenantVolt Electricity Usage API",
    description="API for retrieving electricity usage data from Firebase Realtime Database",
    version="1.0.0"
)

app.include_router(electricity_router, prefix="/electricity", tags=["electricity usage"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to TenantVolt Electricity API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)