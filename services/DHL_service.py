from fastapi import HTTPException
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

DHL_API_KEY = os.getenv("DHL_API_KEY")
DHL_API_SECRET = os.getenv("DHL_API_SECRET")

DHL_API_URL = "https://api.dhl.com/dgff/transportation/shipment-tracking"


# async def create_shipment(order_id: int):
#     headers = {
#         "Content-Type": "application/json",
#         "DHL-API-Key": DHL_API_KEY,
#     }
    
#     shipment_data = {
#         "shipmentRequest": {
#             "shipper": {
#                 "name": "Your Company Name",
#                 "address": {
#                     "street": "Your Street",
#                     "city": "Your City",
#                     "postalCode": "Your Postal Code",
#                     "countryCode": "Your Country Code"
#                 }
#             },
#             "receiver": {
#                 "name": "Client Name",
#                 "address": {
#                     "street": "Client Street",
#                     "city": "Client City",
#                     "postalCode": "Client Postal Code",
#                     "countryCode": "Client Country Code"
#                 }
#             },
#             "packages": [
#                 {
#                     "weight": 5.0,  
#                     "dimensions": {
#                         "length": 30,  
#                         "width": 30,   
#                         "height": 30   
#                     }
#                 }
#             ],
#             "serviceType": "DHL Express Worldwide",  
#         }
#     }
    
#     async with httpx.AsyncClient() as client:
#         response = await client.post(DHL_API_URL, json=shipment_data, headers=headers)

#     if response.status_code != 200:
#         raise HTTPException(
#             status_code=response.status_code,
#             detail=f"Error creating shipment: {response.text}"
#         )

#     data = response.json()

#     if "shipments" not in data or not data["shipments"]:
#         raise HTTPException(
#             status_code=404,
#             detail="Shipment creation failed. No shipments in response."
#         )

#     tracking_number = data["shipments"][0].get("trackingNumber")
    
#     if not tracking_number:
#         raise HTTPException(
#             status_code=404,
#             detail="Tracking number not found in the response."
#         )

#     return tracking_number

async def track_dhl_shipment(tracking_number: str):
    headers = {
        "Content-type": "application/json",
        "DHL-API-Key": DHL_API_KEY,
    }

    params = {
        "trackingNumber": tracking_number,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(DHL_API_URL, params=params, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error calling DHL API")
        
        data = response.json()

        if "shipments" not in data or not data["shipments"]:
            raise HTTPException(status_code=404, detail="Shipment not found")
        
        shipment_status = data["shipment"][0].get("status", "Status not available")
        return shipment_status