import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")
access_token=""
# Get Amadeus token
def get_amadeus_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_API_KEY,
        "client_secret": AMADEUS_API_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=payload, headers=headers)
    access_token = response.json().get("access_token")

    return response.json().get("access_token")


def search_hotels(filters):
    print("🔍 Starting hotel search with filters:", filters)

    # ✅ Validate filters
    if not filters.get("location"):
        return {
            "status": "missing_info",
            "message": "Please specify a location (e.g., Dubai, Paris) to search for hotels."
        }

    if not filters.get("check_in") or not filters.get("check_out"):
        return {
            "status": "missing_info",
            "message": "Please provide both check-in and check-out dates."
        }

    # ✅ Step 1: Get Access Token
    token = get_amadeus_token()
    headers = {"Authorization": f"Bearer {token}"}

    # ✅ Step 2: Fetch Hotels in given location (currently hardcoded DXB for Dubai)
    # If you need dynamic city codes, re-enable location lookup using Amadeus Location API.
    city_code = "DXB" if filters.get("location").lower() == "dubai" else None
    if not city_code:
        return {
            "status": "not_supported",
            "message": f"Currently, we support Dubai only. You entered: {filters.get('location')}"
        }

    hotel_list_url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
    params = {"cityCode": city_code}
    print(f"🏨 Fetching hotels for city code: {city_code}")

    response = requests.get(hotel_list_url, headers=headers, params=params)
    print(f"Hotel List API Status: {response.status_code}")

    if response.status_code != 200:
        return {"error": "Failed to fetch hotels", "details": response.text}

    hotel_data = response.json().get("data", [])
    if not hotel_data:
        return {"status": "no_hotels", "message": "No hotels found for the given city."}

    # ✅ Collect hotel IDs (top 5)
    hotel_ids = [hotel.get("hotelId") for hotel in hotel_data[:5]]
    print(f"✅ Collected Hotel IDs: {hotel_ids}")

    # ✅ Step 3: Get offers (only if check-in & check-out provided)
    offers_url = "https://test.api.amadeus.com/v3/shopping/hotel-offers"
    offer_params = {
        "hotelIds": ",".join(hotel_ids),
        "adults": filters.get("guests") or 1,
        "checkInDate": filters.get("check_in"),
        "checkOutDate": filters.get("check_out"),
        "currency": "USD"
    }
    print(f"💰 Fetching offers for hotels: {hotel_ids}")
    print(f"Offer Params: {offer_params}")

    offers_response = requests.get(offers_url, headers=headers, params=offer_params)
    print(f"Offers API Status: {offers_response.status_code}")

    if offers_response.status_code != 200:
        return {"error": "Failed to fetch hotel offers", "details": offers_response.text}

    offers_data = offers_response.json().get("data", [])
    print(f"✅ Found {len(offers_data)} offers")

    # ✅ Step 4: Format response
    results = []
    for offer in offers_data:
        hotel = offer.get("hotel", {})
        first_offer = offer.get("offers", [{}])[0]
        price = first_offer.get("price", {}).get("total", None)

        results.append({
            "name": hotel.get("name", "Unknown Hotel"),
            "address": hotel.get("address", {}).get("lines", []),
            "price": f"${price}" if price else "Price not available",
            "image": "https://via.placeholder.com/400",
            "bookingUrl": "https://www.thevoyia.com"  # Placeholder
        })

    return {
        "status": "success",
        "message": f"Found {len(results)} hotels in {filters.get('location')}.",
        "hotels": results
    }

def get_hotels_in_dubai():
    token = get_amadeus_token()
    url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
    params = {"cityCode": "DXB"}
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Example usage:
hotels = get_hotels_in_dubai()
