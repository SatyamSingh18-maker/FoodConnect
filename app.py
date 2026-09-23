"""
FoodConnect backend — a small Flask API that:
  - lets donors post surplus food
  - ranks and returns the best nearby NGOs to notify
  - lets an NGO accept a pickup
  - lets an NGO (or volunteer) confirm pickup via QR token

Run locally:
    pip install -r requirements.txt
    python app.py
Then the API is at http://localhost:5000
"""
import uuid
import os
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS

from models import db, NGO, Donation
from matching import rank_ngos_for_donation, expand_search


def create_app(db_uri="sqlite:///foodconnect.db"):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    CORS(app)  # allow the frontend (served from a different origin) to call this API

    with app.app_context():
        db.create_all()
        backfill_qr_tokens()

    register_routes(app)
    return app


def parse_dt(value, field_name):
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError(f"'{field_name}' must be an ISO 8601 datetime, e.g. 2026-07-25T19:40:00")


def parse_coordinate(value, field_name, minimum, maximum):
    try:
        coordinate = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"'{field_name}' must be a number")
    if not minimum <= coordinate <= maximum:
        raise ValueError(f"'{field_name}' must be between {minimum} and {maximum}")
    return coordinate


def ensure_qr_token(donation):
    """Backfill tokens for donations created before QR support was added."""
    if not donation.qr_token:
        donation.qr_token = str(uuid.uuid4())
        return True
    return False


def backfill_qr_tokens():
    """Guarantee every existing donation can be confirmed with a token."""
    donations = Donation.query.filter(
        (Donation.qr_token.is_(None)) | (Donation.qr_token == "")
    ).all()
    if not donations:
        return 0
    for donation in donations:
        ensure_qr_token(donation)
    db.session.commit()
    return len(donations)


def register_routes(app):

    # ---------- health check ----------
    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    # ---------- NGOs ----------
    @app.get("/api/ngos")
    def list_ngos():
        ngos = NGO.query.all()
        return jsonify([n.to_dict() for n in ngos])

    @app.post("/api/ngos")
    def create_ngo():
        data = request.get_json(force=True, silent=True) or {}
        required = ["name", "phone", "lat", "lng"]
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

        try:
            lat = parse_coordinate(data["lat"], "lat", -90, 90)
            lng = parse_coordinate(data["lng"], "lng", -180, 180)
            capacity = int(data.get("capacity", 100))
            response_minutes = int(data.get("avg_response_minutes", 20))
        except (TypeError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400
        if capacity < 0 or response_minutes < 0:
            return jsonify({"error": "capacity and avg_response_minutes cannot be negative"}), 400

        ngo = NGO(
            name=str(data["name"]).strip(),
            phone=str(data["phone"]).strip(),
            lat=lat,
            lng=lng,
            vehicle_available=bool(data.get("vehicle_available", True)),
            capacity=capacity,
            avg_response_minutes=response_minutes,
            verified=bool(data.get("verified", False)),
        )
        db.session.add(ngo)
        db.session.commit()
        return jsonify(ngo.to_dict()), 201

    # ---------- Donations ----------
    @app.post("/api/donations")
    def create_donation():
        data = request.get_json(force=True, silent=True) or {}
        required = ["donor_name", "donor_phone", "location_text", "lat", "lng",
                    "food_type", "quantity_desc", "cooked_time", "pickup_deadline"]
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

        if data["food_type"] not in ("veg", "non-veg"):
            return jsonify({"error": "food_type must be 'veg' or 'non-veg'"}), 400

        try:
            cooked_time = parse_dt(data["cooked_time"], "cooked_time")
            pickup_deadline = parse_dt(data["pickup_deadline"], "pickup_deadline")
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        if pickup_deadline <= cooked_time:
            return jsonify({"error": "pickup_deadline must be after cooked_time"}), 400

        try:
            lat = parse_coordinate(data["lat"], "lat", -90, 90)
            lng = parse_coordinate(data["lng"], "lng", -180, 180)
        except (TypeError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400

        donation = Donation(
            donor_name=str(data["donor_name"]).strip(),
            donor_phone=str(data["donor_phone"]).strip(),
            location_text=str(data["location_text"]).strip(),
            lat=lat,
            lng=lng,
            food_type=data["food_type"],
            quantity_desc=str(data["quantity_desc"]).strip(),
            cooked_time=cooked_time,
            pickup_deadline=pickup_deadline,
            notes=str(data.get("notes", "")),
            photo_url=str(data.get("photo_url", "")),
            qr_token=str(uuid.uuid4()),
        )
        db.session.add(donation)
        db.session.commit()

        # Rank nearby NGOs so the caller (or a background worker) can notify them
        ngos = NGO.query.all()
        top_matches = rank_ngos_for_donation(donation, ngos, top_n=3)

        donation_data = donation.to_dict()
        # Keep the donor-facing token explicit even if models.py omits it from to_dict().
        donation_data["qr_token"] = donation.qr_token

        return jsonify({
            "donation": donation_data,
            "notify": [
                {"ngo": m["ngo"].to_dict(), "distance_km": m["distance_km"]}
                for m in top_matches
            ],
        }), 201

    @app.get("/api/donations")
    def list_donations():
        status = request.args.get("status")
        query = Donation.query
        if status:
            query = query.filter_by(status=status)
        donations = query.order_by(Donation.created_at.desc()).all()
        changed = any(ensure_qr_token(donation) for donation in donations)
        if changed:
            db.session.commit()
        return jsonify([d.to_dict() for d in donations])

    @app.get("/api/donations/<int:donation_id>")
    def get_donation(donation_id):
        donation = Donation.query.get(donation_id)
        if not donation:
            return jsonify({"error": "Donation not found"}), 404
        if ensure_qr_token(donation):
            db.session.commit()
        return jsonify(donation.to_dict())

    @app.post("/api/donations/<int:donation_id>/accept")
    def accept_donation(donation_id):
        data = request.get_json(force=True, silent=True) or {}
        ngo_id = data.get("ngo_id")
        token = data.get("qr_token")
        if not ngo_id:
            return jsonify({"error": "ngo_id is required"}), 400

        donation = Donation.query.get(donation_id)
        if not donation:
            return jsonify({"error": "Donation not found"}), 404
        if ensure_qr_token(donation):
            db.session.commit()
        if donation.status != "open":
            return jsonify({"error": f"Donation is already '{donation.status}'"}), 409
        # Older clients may still send the token during acceptance. Validate it
        # when present, but acceptance itself does not require a scan.
        if token and token != donation.qr_token:
            return jsonify({"error": "Pickup token does not match this donation"}), 403

        ngo = NGO.query.get(ngo_id)
        if not ngo:
            return jsonify({"error": "NGO not found"}), 404

        donation.status = "accepted"
        donation.accepted_by_ngo_id = ngo.id
        donation.accepted_at = datetime.utcnow()
        db.session.commit()

        accepted_data = donation.to_dict()
        accepted_data["qr_token"] = donation.qr_token
        return jsonify(accepted_data)

    @app.post("/api/donations/<int:donation_id>/confirm-pickup")
    def confirm_pickup(donation_id):
        """Simulates scanning the QR code at pickup time."""
        data = request.get_json(force=True, silent=True) or {}
        token = str(data.get("qr_token") or "").strip()

        donation = Donation.query.get(donation_id)
        if not donation:
            return jsonify({"error": "Donation not found"}), 404
        if ensure_qr_token(donation):
            db.session.commit()
        if donation.status != "accepted":
            return jsonify({"error": f"Donation must be 'accepted' first, is '{donation.status}'"}), 409
        if token != donation.qr_token:
            return jsonify({"error": "Invalid pickup token."}), 403

        donation.status = "completed"
        db.session.commit()
        return jsonify(donation.to_dict())

    @app.post("/api/donations/<int:donation_id>/expand-search")
    def expand_donation_search(donation_id):
        """If no NGO has accepted yet, widen the radius and return the next candidates."""
        data = request.get_json(force=True, silent=True) or {}
        already_notified = data.get("already_notified_ngo_ids", [])

        donation = Donation.query.get(donation_id)
        if not donation:
            return jsonify({"error": "Donation not found"}), 404

        ngos = NGO.query.all()
        matches, radius_used = expand_search(donation, ngos, set(already_notified))
        return jsonify({
            "radius_km": radius_used,
            "notify": [
                {"ngo": m["ngo"].to_dict(), "distance_km": m["distance_km"]}
                for m in matches
            ],
        })

    # ---------- Analytics (matches the spec's dashboard) ----------
    @app.get("/api/analytics")
    def analytics():
        total = Donation.query.count()
        completed = Donation.query.filter_by(status="completed").count()
        open_now = Donation.query.filter_by(status="open").count()
        accepted = Donation.query.filter_by(status="accepted").count()
        return jsonify({
            "total_donations": total,
            "completed": completed,
            "open": open_now,
            "accepted": accepted,
        })


app = create_app()

if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )

