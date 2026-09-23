"""
Database models for FoodConnect.

Donation  -> a surplus-food post from a donor
NGO       -> an organization that can accept and pick up donations
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class NGO(db.Model):
    __tablename__ = "ngos"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    vehicle_available = db.Column(db.Boolean, default=True)
    capacity = db.Column(db.Integer, default=100)
    avg_response_minutes = db.Column(db.Integer, default=20)
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "lat": self.lat,
            "lng": self.lng,
            "vehicle_available": self.vehicle_available,
            "capacity": self.capacity,
            "avg_response_minutes": self.avg_response_minutes,
            "verified": self.verified,
        }


class Donation(db.Model):
    __tablename__ = "donations"

    id = db.Column(db.Integer, primary_key=True)
    donor_name = db.Column(db.String(120), nullable=False)
    donor_phone = db.Column(db.String(20), nullable=False)
    location_text = db.Column(db.String(255), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    food_type = db.Column(db.String(10), nullable=False)
    quantity_desc = db.Column(db.String(120), nullable=False)
    cooked_time = db.Column(db.DateTime, nullable=False)
    pickup_deadline = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text, default="")
    photo_url = db.Column(db.String(255), default="")

    # open -> accepted -> completed (or expired if deadline passes unclaimed)
    status = db.Column(db.String(20), default="open")
    accepted_by_ngo_id = db.Column(db.Integer, db.ForeignKey("ngos.id"), nullable=True)
    accepted_at = db.Column(db.DateTime, nullable=True)

    # Generated when the donor posts the donation.
    # The NGO pastes it to accept, and it is checked again at pickup confirmation.
    qr_token = db.Column(db.String(36), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    accepted_by = db.relationship("NGO", foreign_keys=[accepted_by_ngo_id])

    def to_dict(self):
        return {
            "id": self.id,
            "donor_name": self.donor_name,
            "donor_phone": self.donor_phone,
            "location_text": self.location_text,
            "lat": self.lat,
            "lng": self.lng,
            "food_type": self.food_type,
            "quantity_desc": self.quantity_desc,
            "cooked_time": self.cooked_time.isoformat(),
            "pickup_deadline": self.pickup_deadline.isoformat(),
            "notes": self.notes,
            "photo_url": self.photo_url,
            "status": self.status,
            "accepted_by_ngo_id": self.accepted_by_ngo_id,
            "accepted_by_ngo_name": self.accepted_by.name if self.accepted_by else None,
            "qr_token": self.qr_token,
            "created_at": self.created_at.isoformat(),
        }

