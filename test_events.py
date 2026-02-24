import requests
import json
import uuid

BASE_URL = 'http://127.0.0.1:8000/app1/event-bookings/'
ref = str(uuid.uuid4())[:8]

payload = {
    "name": "Test Multi-Session Event",
    "mobile_no": "1234567890",
    "reference": ref,
    "advance_amount": "5000",
    "advance_payment_mode": "CASH",
    "description": "2 days event",
    "status": "pending",
    "sessions": [
        {
            "event_date": "25-02-2026",
            "event_time": "Morning Breakfast",
            "event_address": "Hall A",
            "per_dish_amount": "200",
            "estimated_persons": "100",
            "selected_items": {
                "Breakfast": ["Tea", "Idli"]
            },
            "extra_service": [
                {"name": "DJ", "amount": "1000", "extra": True}
            ]
        },
        {
            "event_date": "26-02-2026",
            "event_time": "Dinner Party",
            "event_address": "Hall B",
            "per_dish_amount": "500",
            "estimated_persons": "150",
            "selected_items": {
                "Starters": ["Paneer Tikka"],
                "Mains": ["Dal Makhani", "Naan"]
            },
            "extra_service": [
                {"name": "Decoration", "amount": "5000", "extra": True}
            ]
        }
    ]
}

print("Creating Event Booking...")
response = requests.post(BASE_URL, json=payload)
data = response.json()
print("Create Status:", response.status_code)
print(json.dumps(data, indent=2))

if data.get("status"):
    booking_id = data["data"]["id"]
    
    print("\nGetting Booking by ID...")
    get_res = requests.get(f"{BASE_URL}{booking_id}/")
    print("Get Status:", get_res.status_code)
    print(json.dumps(get_res.json(), indent=2))
    
    print("\nUpdating Booking...")
    update_payload = {
        "sessions": [
            {
                "event_date": "25-02-2026",
                "event_time": "Updated Morning Breakfast",
                "event_address": "Hall C",
                "per_dish_amount": "250",
                "estimated_persons": "120",
                "selected_items": {
                    "Breakfast": ["Coffee", "Dosa"]
                },
                "extra_service": []
            }
        ]
    }
    update_res = requests.put(f"{BASE_URL}{booking_id}/", json=update_payload)
    print("Update Status:", update_res.status_code)
    print(json.dumps(update_res.json(), indent=2))
