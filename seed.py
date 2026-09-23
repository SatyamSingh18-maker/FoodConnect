"""
Adds a few sample NGOs so you have something to test matching against.
Run: python seed.py
"""
from app import create_app
from models import db, NGO

app = create_app()

SAMPLE_NGOS = [
    {"name": "Helping Hands", "phone": "+91 9800000001", "lat": 19.0760, "lng": 72.8777,
     "vehicle_available": True, "capacity": 300, "avg_response_minutes": 12, "verified": True},
    {"name": "Feed the City", "phone": "+91 9800000002", "lat": 19.0896, "lng": 72.8656,
     "vehicle_available": True, "capacity": 150, "avg_response_minutes": 18, "verified": True},
    {"name": "Seva Kitchen", "phone": "+91 9800000003", "lat": 19.0330, "lng": 72.8570,
     "vehicle_available": False, "capacity": 200, "avg_response_minutes": 25, "verified": True},
    {"name": "Annapurna Trust", "phone": "+91 9800000004", "lat": 19.1197, "lng": 72.9050,
     "vehicle_available": True, "capacity": 0, "avg_response_minutes": 15, "verified": True},
    {"name": "New Hope Foundation", "phone": "+91 9800000005", "lat": 19.0176, "lng": 72.8562,
     "vehicle_available": True, "capacity": 100, "avg_response_minutes": 30, "verified": False},
]

with app.app_context():
    if NGO.query.count() == 0:
        for entry in SAMPLE_NGOS:
            db.session.add(NGO(**entry))
        db.session.commit()
        print(f"Seeded {len(SAMPLE_NGOS)} NGOs.")
    else:
        print("NGOs already exist, skipping seed.")
