from fastapi import HTTPException
from sqlalchemy.orm import Session
import httpx
from dotenv import load_dotenv
import os
import models

load_dotenv()

DHL_API_KEY = os.getenv("DHL_API_KEY")
DHL_API_SECRET = os.getenv("DHL_API_SECRET")

DHL_API_URL_CREATE = "https://api-sandbox.dhl.com/dgff/transportation/shipment-booking"
DHL_API_URL_TRACK = "https://api-sandbox.dhl.com/dgff/transportation/v2/shipment-tracking"


async def create_shipment(order_id: int, db: Session):
    headers = {
        "Content-Type": "application/json",
        "DHL-API-Key": DHL_API_KEY,
    }

    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=404, 
            detail="Order not found"
        )
    
    shipment_data = {
        "shipmentRequest": {
            "shipper": {
            "name": "Test Company",
            "address": {
                "street": "123 Fake St",
                "city": "Faketown",
                "postalCode": "12345",
                "countryCode": "US"
            }
            },
            "receiver": {
            "name": "Test Receiver",
            "address": {
                "street": "456 Test Ave",
                "city": "Test City",
                "postalCode": "67890",
                "countryCode": "US"
            }
            },
            "packages": [
            {
                "weight": 2.0,
                "dimensions": {
                "length": 30,
                "width": 30,
                "height": 30
                }
            }
            ],
            "serviceType": "DHL Express Worldwide"
        }
}

    
    async with httpx.AsyncClient() as client:
        response = await client.post(DHL_API_URL_CREATE, json=shipment_data, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error creating shipment: {response.text}"
        )

    data = response.json()

    if "shipments" not in data or not data["shipments"]:
        raise HTTPException(
            status_code=404,
            detail="Shipment creation failed. No shipments in response."
        )

    tracking_number = data["shipments"][0].get("trackingNumber")
    
    if not tracking_number:
        raise HTTPException(
            status_code=404,
            detail="Tracking number not found in the response."
        )

    return tracking_number

async def track_dhl_shipment(tracking_number: str):
    headers = {
        "Content-type": "application/json",
        "DHL-API-Key": DHL_API_KEY,
    }

    params = {
        "trackingNumber": tracking_number,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(DHL_API_URL_TRACK, params=params, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error calling DHL API")
        
        data = response.json()

        if "shipments" not in data or not data["shipments"]:
            raise HTTPException(status_code=404, detail="Shipment not found")
        
        shipment_status = data["shipments"][0].get("status", "Status not available")
        return shipment_status