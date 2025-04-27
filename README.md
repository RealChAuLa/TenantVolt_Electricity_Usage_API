# TenantVolt Electricity Usage API

## Overview

TenantVolt Electricity Usage API provides access to electricity consumption data stored in Firebase Realtime Database. This API allows users to retrieve electricity usage statistics at various time intervals (minutely, hourly, daily, and monthly) and manage connection status information for tenant devices.

## Endpoints

### Electricity Usage

#### Get Minutely Usage

```
GET /electricity/minutely/{product_id}/{date}/{hour}
```

Retrieves minute-by-minute electricity usage for a specific hour in a day.

**Parameters:**
- `product_id` (path, required): The product identifier
- `date` (path, required): Date in YYYY-MM-DD format
- `hour` (path, required): Hour in HH format (00-23)

**Response:**
- 200: Returns data for chart where X-axis shows minutes (00-59) and Y-axis shows average watt values
- 422: Validation Error

#### Get Hourly Usage

```
GET /electricity/hourly/{product_id}/{date}
```

Retrieves hourly electricity usage for a specific day.

**Parameters:**
- `product_id` (path, required): The product identifier
- `date` (path, required): Date in YYYY-MM-DD format

**Response:**
- 200: Returns data for chart where X-axis shows hours (00-23) and Y-axis shows average watt values
- 422: Validation Error

#### Get Daily Usage

```
GET /electricity/daily/{product_id}/{year_month}
```

Retrieves daily electricity usage for a specific month.

**Parameters:**
- `product_id` (path, required): The product identifier
- `year_month` (path, required): Year and month in YYYY-MM format

**Response:**
- 200: Returns data for chart where X-axis shows days (01-31) and Y-axis shows average watt values
- 422: Validation Error

#### Get Monthly Usage

```
GET /electricity/monthly/{product_id}/{year}
```

Retrieves monthly electricity usage for a specific year.

**Parameters:**
- `product_id` (path, required): The product identifier
- `year` (path, required): Year in YYYY format

**Response:**
- 200: Returns data for chart where X-axis shows months (01-12) and Y-axis shows average watt values
- 422: Validation Error

### Connection Status

#### Get Connection Status

```
POST /electricity/connection-status
```

Retrieves the connection status for each product ID in the request.

**Request Body:**
```json
{
  "tenants": [
    {
      "tenant_index": 0,
      "product_id": "string"
    }
  ]
}
```

**Response:**
- 200: Returns connection status for each tenant
- 422: Validation Error

#### Update Connection Status

```
POST /electricity/update-connection-status
```

Updates the connection status for a specific product ID.

**Request Body:**
```json
{
  "connection_status": true,
  "product_id": "string"
}
```

**Response:**
- 200: Returns success message
- 422: Validation Error

### Electricity Bills

#### Get Latest Bill Details

```
POST /bill/latest
```

Retrieves the latest bill details for each tenant's product ID by finding the most recent month in the electricity_bills/{product_id} directory.

**Request Body:**
```json
{
  "tenants": [
    {
      "tenant_index": 0,
      "product_id": "string",
      "bill_details": {
        "additionalProp1": {}
      }
    }
  ]
}
```

**Response:**
- 200: Returns the latest bill details for each tenant
- 422: Validation Error

### Default Endpoints

#### Root

```
GET /
```

Root endpoint for the API.

**Response:**
- 200: Returns a welcome message

#### Debug Time

```
GET /debug/time
```

Endpoint for debugging time-related functionality.

**Response:**
- 200: Returns current time information

## Data Models

### ChartDataPoint
```json
{
  "label": "string",
  "value": 0
}
```

### ChartDataResponse
```json
{
  "data_points": [
    {
      "label": "string",
      "value": 0
    }
  ],
  "chart_title": "string",
  "x_axis_label": "string",
  "y_axis_label": "Power Consumption (W)"
}
```

### ConnectionStatusUpdate
```json
{
  "connection_status": boolean,
  "product_id": "string"
}
```

### Tenant
```json
{
  "tenant_index": integer,
  "product_id": "string",
  "bill_details": object | null
}
```

### TenantRequest
```json
{
  "tenant_index": integer,
  "product_id": "string"
}
```

### TenantStatusResponse
```json
{
  "tenant_index": integer,
  "connection_status": boolean
}
```

### TenantsListRequest
```json
{
  "tenants": [
    {
      "tenant_index": integer,
      "product_id": "string"
    }
  ]
}
```

## Installation

This API is built with FastAPI. To run it locally:

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Start the server:
   ```
   uvicorn app.main:app --reload
   ```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`
