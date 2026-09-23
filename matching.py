"""
Smart NGO matching, as described in the project spec:
rank candidate NGOs by distance, vehicle availability, capacity,
and historical response time. Return the top N to notify first.
"""
from math import radians, sin, cos, sqrt, atan2


def haversine_km(lat1, lng1, lat2, lng2):
    """Great-circle distance between two lat/lng points, in km."""
    R = 6371.0
    p1, p2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lng2 - lng1)
    a = sin(dphi / 2) ** 2 + cos(p1) * cos(p2) * sin(dlambda / 2) ** 2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


def rank_ngos_for_donation(donation, ngos, top_n=3, max_radius_km=None):
    """
    Rank NGOs for a given donation.

    Filters out NGOs with no vehicle or no capacity, then sorts by:
      1. distance (closer is better)
      2. average response time (faster is better)

    Returns a list of dicts: {ngo, distance_km} sorted best-first,
    optionally limited to those within max_radius_km.
    """
    candidates = []
    for ngo in ngos:
        if not ngo.vehicle_available or ngo.capacity <= 0 or not ngo.verified:
            continue
        distance = haversine_km(donation.lat, donation.lng, ngo.lat, ngo.lng)
        if max_radius_km is not None and distance > max_radius_km:
            continue
        candidates.append({"ngo": ngo, "distance_km": round(distance, 2)})

    candidates.sort(key=lambda c: (c["distance_km"], c["ngo"].avg_response_minutes))
    return candidates[:top_n]


def expand_search(donation, ngos, already_notified_ids, radius_step_km=5, max_radius_km=25):
    """
    If nobody has accepted yet, widen the search radius and return
    the next batch of NGOs not already notified. Mirrors the spec's
    'expand radius, then alert volunteers' escalation flow.
    """
    for radius in range(radius_step_km, max_radius_km + 1, radius_step_km):
        ranked = rank_ngos_for_donation(donation, ngos, top_n=10, max_radius_km=radius)
        fresh = [c for c in ranked if c["ngo"].id not in already_notified_ids]
        if fresh:
            return fresh, radius
    return [], max_radius_km
