import os
from datetime import date, datetime, time, timedelta, timezone
from io import BytesIO
from zoneinfo import ZoneInfo

import qrcode
import requests
import streamlit as st


API_BASE = os.getenv("FOODCONNECT_API_URL", "http://127.0.0.1:5000").rstrip("/")
try:
    API_BASE = str(st.secrets.get("FOODCONNECT_API_URL", API_BASE)).rstrip("/")
except Exception:
    pass

PAGES = [
    "About Us",
    "Home",
    "Donate Food",
    "Register NGO",
    "NGO Directory",
    "NGO Pickup",
    "Donation History",
    "Analytics",
]
STATUS_OPTIONS = ["all", "open", "accepted", "completed", "expired"]
STATUS_LABELS = {
    "open": "Open",
    "accepted": "Accepted",
    "completed": "Completed",
    "expired": "Expired",
}

st.set_page_config(page_title="FoodConnect", page_icon="🥬", layout="wide")
st.markdown(
    """
    <style>
      :root { color-scheme: dark; }
      .stApp { background: #101a17; color: #f3f7f2; }
      [data-testid="stSidebar"] { background: #0b1311; border-right: 1px solid #29362f; }
      h1, h2, h3 { letter-spacing: -0.025em; }
      .eyebrow { color: #b9f44b; font-size: .72rem; font-weight: 800; letter-spacing: .12em; }
      .lead { color: #bdc8c1; font-size: 1.05rem; line-height: 1.65; max-width: 780px; }
      .surface { border: 1px solid #29362f; border-radius: 10px; padding: 1rem 1.15rem; background: #17231e; margin: .4rem 0 1rem; }
      .muted { color: #9ca9a2; font-size: .9rem; }
      .status { display: inline-block; padding: .2rem .5rem; border-radius: 4px; font-size: .72rem; font-weight: 800; text-transform: uppercase; }
      .status-open { background: #34452b; color: #d9f7a5; }
      .status-accepted { background: #51452a; color: #ffe39b; }
      .status-completed { background: #24483c; color: #a4e9d3; }
      .status-expired { background: #552d29; color: #ffc5bb; }
      div.stButton > button[kind="primary"] { background: #b9f44b; color: #101a17; border: 0; font-weight: 800; }
      div.stButton > button { border-radius: 7px; }
      [data-testid="stMetric"] { border: 1px solid #29362f; background: #17231e; padding: .85rem; border-radius: 8px; }
      [data-testid="stMetricValue"] { color: #b9f44b; }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_request(method, path, **kwargs):
    try:
        response = requests.request(
            method,
            f"{API_BASE}{path}",
            timeout=15,
            **kwargs,
        )
    except requests.RequestException as exc:
        return None, f"Cannot reach the FoodConnect API at {API_BASE}: {exc}"

    try:
        payload = response.json()
    except ValueError:
        payload = {}
    if not response.ok:
        return None, payload.get("error", f"API request failed ({response.status_code}).")
    return payload, None


def get_api(path, **kwargs):
    return api_request("GET", path, **kwargs)


def post_api(path, payload):
    return api_request("POST", path, json=payload)


def show_error(error):
    if error:
        st.error(error)


def status_badge(status):
    label = STATUS_LABELS.get(status, status.title())
    st.markdown(
        f'<span class="status status-{status}">{label}</span>',
        unsafe_allow_html=True,
    )


def qr_image(token):
    image = qrcode.make(token)
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def decode_qr_image(image_bytes):
    import cv2
    import numpy as np

    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if image is None:
        return ""
    decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(image)
    return decoded.strip()


def utc_iso(day_value, time_value, zone_name):
    local_value = datetime.combine(day_value, time_value).replace(
        tzinfo=ZoneInfo(zone_name)
    )
    return local_value.astimezone(timezone.utc).isoformat()


def render_about():
    st.markdown('<p class="eyebrow">ABOUT FOODCONNECT</p>', unsafe_allow_html=True)
    st.title("Good food deserves a better destination.")
    st.markdown(
        '<p class="lead">FoodConnect connects surplus food with nearby NGOs so useful meals reach communities instead of going to waste.</p>',
        unsafe_allow_html=True,
    )
    st.divider()
    left, right = st.columns(2)
    with left:
        st.subheader("Our purpose")
        st.write("Turn surplus into shared value. Donors can offer food to local organizations that can collect and distribute it.")
    with right:
        st.subheader("How we help")
        st.write("Location-based matching, clear donation statuses, and QR-verified collection make handoffs easier to coordinate.")
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Local matching", "Nearby NGOs")
    c2.metric("Verified handoffs", "QR pickup")
    c3.metric("Shared outcome", "Less food waste")
    return st.button("Explore FoodConnect", type="primary")


def render_home(navigate):
    st.markdown('<p class="eyebrow">SURPLUS FOOD RESCUE PLATFORM</p>', unsafe_allow_html=True)
    st.title("Good food. Less waste. More hope.")
    st.markdown(
        '<p class="lead">Connect surplus food with NGOs. FoodConnect helps donors rescue usable food and makes pickup traceable and reliable.</p>',
        unsafe_allow_html=True,
    )
    total_col, open_col, accepted_col, completed_col = st.columns(4)
    analytics, error = get_api("/api/analytics")
    if error:
        show_error(error)
    else:
        total_col.metric("Donations", analytics["total_donations"])
        open_col.metric("Open", analytics["open"])
        accepted_col.metric("Accepted", analytics["accepted"])
        completed_col.metric("Completed", analytics["completed"])
    st.divider()
    st.subheader("Choose where to begin")
    cols = st.columns(3)
    for col, page, title, copy in zip(
        cols,
        ["Donate Food", "NGO Pickup", "Analytics"],
        ["Share surplus food", "Coordinate a pickup", "See the impact"],
        ["Post a pickup-ready donation.", "Accept and verify collection.", "Review live donation activity."],
    ):
        with col:
            st.markdown(f'<div class="surface"><h3>{title}</h3><p class="muted">{copy}</p></div>', unsafe_allow_html=True)
            if st.button(f"Open {page}", key=f"home-{page}"):
                navigate(page)


def render_donation_form():
    st.markdown('<p class="eyebrow">DONATE SURPLUS</p>', unsafe_allow_html=True)
    st.title("Donate Food")
    st.write("Share what you have and where it can be collected. Nearby NGOs are matched after posting.")
    if "last_donation" not in st.session_state:
        st.session_state.last_donation = None

    with st.form("donation-form"):
        donor_col, phone_col = st.columns(2)
        donor_name = donor_col.text_input("Donor name", max_chars=120)
        donor_phone = phone_col.text_input("Phone number", max_chars=20)
        location = st.text_input("Pickup address", max_chars=255)
        latitude_col, longitude_col = st.columns(2)
        latitude = latitude_col.number_input("Latitude", min_value=-90.0, max_value=90.0, value=19.0760, format="%.6f")
        longitude = longitude_col.number_input("Longitude", min_value=-180.0, max_value=180.0, value=72.8777, format="%.6f")
        food_col, quantity_col = st.columns(2)
        food_type = food_col.selectbox("Food type", ["veg", "non-veg"], format_func=lambda value: "Vegetarian" if value == "veg" else "Non-vegetarian")
        quantity = quantity_col.text_input("Quantity", placeholder="e.g. 20 meal portions", max_chars=120)
        zone_name = st.selectbox("Time zone", ["Asia/Kolkata", "UTC"])
        now_local = datetime.now(ZoneInfo(zone_name))
        cooked_date_col, cooked_time_col = st.columns(2)
        cooked_date = cooked_date_col.date_input("Prepared date", value=now_local.date())
        cooked_time = cooked_time_col.time_input("Prepared time", value=now_local.time().replace(tzinfo=None, second=0, microsecond=0))
        deadline_date_col, deadline_time_col = st.columns(2)
        deadline_date = deadline_date_col.date_input("Pickup deadline date", value=(now_local + timedelta(hours=4)).date())
        deadline_time = deadline_time_col.time_input("Pickup deadline time", value=(now_local + timedelta(hours=4)).time().replace(tzinfo=None, second=0, microsecond=0))
        notes = st.text_area("Additional notes (optional)", max_chars=2000)
        submitted = st.form_submit_button("Post donation", type="primary", use_container_width=True)

    if submitted:
        if not all([donor_name.strip(), donor_phone.strip(), location.strip(), quantity.strip()]):
            st.error("Fill in the donor, contact, address, and quantity fields.")
        else:
            payload = {
                "donor_name": donor_name.strip(),
                "donor_phone": donor_phone.strip(),
                "location_text": location.strip(),
                "lat": latitude,
                "lng": longitude,
                "food_type": food_type,
                "quantity_desc": quantity.strip(),
                "cooked_time": utc_iso(cooked_date, cooked_time, zone_name),
                "pickup_deadline": utc_iso(deadline_date, deadline_time, zone_name),
                "notes": notes.strip(),
            }
            result, error = post_api("/api/donations", payload)
            if error:
                st.error(error)
            else:
                st.session_state.last_donation = result
                st.success(f"Donation #{result['donation']['id']} posted and open for pickup.")

    result = st.session_state.last_donation
    if result:
        donation = result["donation"]
        st.divider()
        st.subheader(f"Donation #{donation['id']} · Pickup credentials")
        qr_col, detail_col = st.columns([1, 2])
        with qr_col:
            st.image(qr_image(donation["qr_token"]), width=190)
        with detail_col:
            st.code(donation["qr_token"], language=None)
            st.caption("Show this QR or share the token with the accepting NGO.")
            matches = result.get("notify", [])
            st.markdown("**Nearby NGO matches**")
            if matches:
                for match in matches:
                    st.write(f"{match['ngo']['name']} · {match['distance_km']:.1f} km")
            else:
                st.info("No nearby NGOs matched yet.")


def render_register_ngo():
    st.markdown('<p class="eyebrow">JOIN THE RESCUE NETWORK</p>', unsafe_allow_html=True)
    st.title("Register NGO")
    st.write("Share your organization’s location and pickup capacity so donors can find you.")
    with st.form("ngo-registration"):
        name_col, phone_col = st.columns(2)
        name = name_col.text_input("Organization name", max_chars=120)
        phone = phone_col.text_input("Contact phone", max_chars=20)
        lat_col, lng_col = st.columns(2)
        lat = lat_col.number_input("Latitude", min_value=-90.0, max_value=90.0, value=19.0760, format="%.6f")
        lng = lng_col.number_input("Longitude", min_value=-180.0, max_value=180.0, value=72.8777, format="%.6f")
        capacity_col, response_col = st.columns(2)
        capacity = capacity_col.number_input("Pickup capacity", min_value=0, value=100, step=1)
        response_minutes = response_col.number_input("Average response time (minutes)", min_value=0, value=20, step=1)
        vehicle = st.checkbox("Pickup vehicle available", value=True)
        submitted = st.form_submit_button("Register organization", type="primary")
    if submitted:
        payload = {
            "name": name.strip(), "phone": phone.strip(), "lat": lat, "lng": lng,
            "capacity": capacity, "avg_response_minutes": response_minutes,
            "vehicle_available": vehicle,
        }
        if not payload["name"] or not payload["phone"]:
            st.error("Organization name and contact phone are required.")
            return
        result, error = post_api("/api/ngos", payload)
        if error:
            st.error(error)
        else:
            verification = "verified" if result["verified"] else "pending review"
            st.success(f"{result['name']} registered; status is {verification}.")


def render_directory():
    st.markdown('<p class="eyebrow">COMMUNITY PARTNERS</p>', unsafe_allow_html=True)
    st.title("NGO Directory")
    ngos, error = get_api("/api/ngos")
    if error:
        show_error(error)
        return
    query = st.text_input("Search organizations", placeholder="Search by NGO name")
    matches = [ngo for ngo in ngos if query.casefold() in ngo["name"].casefold()]
    if not matches:
        st.info("No organizations match that search." if ngos else "No NGOs are registered yet.")
        return
    columns = st.columns(2)
    for index, ngo in enumerate(matches):
        with columns[index % 2]:
            with st.container(border=True):
                status = "Verified" if ngo["verified"] else "Pending review"
                st.subheader(ngo["name"])
                st.caption(f"{status} · {ngo['phone']}")
                st.write(f"Coordinates: {ngo['lat']:.4f}, {ngo['lng']:.4f}")
                st.write(f"Capacity: {ngo['capacity']} · Response: {ngo['avg_response_minutes']} min")
                st.write("Vehicle available" if ngo["vehicle_available"] else "No vehicle listed")
                st.link_button("Open map", f"https://www.google.com/maps?q={ngo['lat']},{ngo['lng']}")


def render_pickups():
    st.markdown('<p class="eyebrow">NGO OPERATIONS</p>', unsafe_allow_html=True)
    st.title("NGO Pickup")
    st.write("Accept available donations and verify collection with the donor’s pickup token.")
    ngos, ngo_error = get_api("/api/ngos")
    donations, donation_error = get_api("/api/donations")
    if ngo_error or donation_error:
        show_error(ngo_error or donation_error)
        return
    if not ngos:
        st.info("Register an NGO before accepting pickup requests.")
        return
    ngo_by_id = {ngo["id"]: ngo for ngo in ngos}
    selected_id = st.selectbox(
        "Operating NGO",
        options=list(ngo_by_id),
        format_func=lambda ngo_id: ngo_by_id[ngo_id]["name"] + (" · Verified" if ngo_by_id[ngo_id]["verified"] else ""),
    )
    counts = {status: sum(item["status"] == status for item in donations) for status in STATUS_OPTIONS[1:]}
    filter_status = st.radio(
        "Filter donations",
        STATUS_OPTIONS,
        format_func=lambda value: "All" if value == "all" else f"{STATUS_LABELS[value]} ({counts[value]})",
        horizontal=True,
    )
    visible = [item for item in donations if filter_status == "all" or item["status"] == filter_status]
    if not visible:
        st.info("No donations in this status yet.")
        return

    for donation in visible:
        with st.container(border=True):
            header_col, status_col = st.columns([4, 1])
            header_col.subheader(donation["quantity_desc"])
            status_col.markdown(f'<span class="status status-{donation["status"]}">{donation["status"]}</span>', unsafe_allow_html=True)
            st.write(f"{donation['food_type'].replace('-', ' ').title()} · Donated by {donation['donor_name']}")
            st.write(f"Pickup: {donation['location_text']}")
            st.caption(f"Pickup before {donation['pickup_deadline']}")
            if donation.get("accepted_by_ngo_name"):
                st.info(f"Accepted by {donation['accepted_by_ngo_name']}")

            if donation["status"] == "open":
                if st.button("Accept pickup", key=f"accept-{donation['id']}", type="primary"):
                    result, error = post_api(
                        f"/api/donations/{donation['id']}/accept",
                        {"ngo_id": selected_id},
                    )
                    if error:
                        st.error(error)
                    else:
                        st.success(f"Donation #{donation['id']} accepted by {result.get('accepted_by_ngo_name', ngo_by_id[selected_id]['name'])}.")
                        st.rerun()
            elif donation["status"] == "accepted":
                credential_col, confirm_col = st.columns([1, 2])
                with credential_col:
                    st.image(qr_image(donation["qr_token"]), width=170)
                with confirm_col:
                    st.markdown(f"**Accepted by {donation.get('accepted_by_ngo_name') or 'NGO'}**")
                    st.code(donation["qr_token"], language=None)
                    token_key = f"token-{donation['id']}"
                    captured_qr = st.camera_input("Scan pickup QR", key=f"camera-{donation['id']}")
                    if captured_qr:
                        try:
                            decoded_token = decode_qr_image(captured_qr.getvalue())
                            if decoded_token:
                                st.session_state[token_key] = decoded_token
                                st.success("QR token scanned.")
                            else:
                                st.warning("No QR token was detected. Try again or enter the token manually.")
                        except ImportError:
                            st.warning("Camera QR scanning is unavailable; enter the token manually.")
                    token = st.text_input("Pickup token", key=token_key, placeholder="Scan QR or enter token")
                    if st.button("Confirm pickup", key=f"confirm-{donation['id']}", type="primary"):
                        result, error = post_api(
                            f"/api/donations/{donation['id']}/confirm-pickup",
                            {"qr_token": token.strip()},
                        )
                        if error:
                            st.error(error)
                        else:
                            st.success(f"Pickup #{donation['id']} completed.")
                            st.rerun()
            elif donation["status"] == "expired":
                st.warning("Pickup deadline passed before collection. This donation can no longer be accepted or confirmed.")


def render_history():
    st.markdown('<p class="eyebrow">TRACEABLE FOOD RESCUE</p>', unsafe_allow_html=True)
    st.title("Donation History")
    donations, error = get_api("/api/donations")
    if error:
        show_error(error)
        return
    status = st.selectbox("Status", STATUS_OPTIONS, format_func=lambda value: "All" if value == "all" else STATUS_LABELS[value])
    visible = [item for item in donations if status == "all" or item["status"] == status]
    st.caption(f"{len(visible)} donation records")
    for donation in visible:
        with st.container(border=True):
            cols = st.columns([3, 1])
            cols[0].subheader(donation["quantity_desc"])
            cols[1].markdown(f'<span class="status status-{donation["status"]}">{donation["status"]}</span>', unsafe_allow_html=True)
            st.write(f"{donation['food_type'].replace('-', ' ').title()} · {donation['donor_name']}")
            st.write(donation["location_text"])
            st.caption(f"Posted {donation['created_at']} · Pickup deadline {donation['pickup_deadline']}")
            if donation.get("accepted_by_ngo_name"):
                st.caption(f"Accepted by {donation['accepted_by_ngo_name']}")
            if donation["status"] == "expired":
                st.warning("Pickup deadline passed before collection.")


def render_analytics():
    st.markdown('<p class="eyebrow">LIVE REPORTING</p>', unsafe_allow_html=True)
    st.title("Analytics")
    analytics, error = get_api("/api/analytics")
    if error:
        show_error(error)
        return
    columns = st.columns(5)
    columns[0].metric("Total donations", analytics["total_donations"])
    columns[1].metric("Open", analytics["open"])
    columns[2].metric("Accepted", analytics["accepted"])
    columns[3].metric("Completed", analytics["completed"])
    columns[4].metric("Expired", analytics.get("expired", 0))
    st.subheader("Donation status")
    st.bar_chart(
        {
            "Donations": {
                "Open": analytics["open"],
                "Accepted": analytics["accepted"],
                "Completed": analytics["completed"],
                "Expired": analytics.get("expired", 0),
            }
        },
        horizontal=True,
    )
    total = analytics["total_donations"]
    completed_rate = round(analytics["completed"] / total * 100) if total else 0
    st.metric("Completion rate", f"{completed_rate}%")


def main():
    requested_page = st.query_params.get("page", "About Us")
    if requested_page in PAGES:
        st.session_state["page_nav"] = requested_page

    def sync_navigation():
        st.query_params["page"] = st.session_state["page_nav"]

    def navigate(target):
        st.query_params["page"] = target
        st.rerun()

    with st.sidebar:
        st.markdown("## 🥬 FoodConnect")
        st.caption("Good food · Less waste · More hope")
        page = st.radio("Navigate", PAGES, key="page_nav", on_change=sync_navigation, label_visibility="collapsed")
        st.divider()
        st.caption("Connected API")
        st.code(API_BASE, language=None)

    if page == "About Us":
        if render_about():
            navigate("Home")
    elif page == "Home":
        render_home(navigate)
    elif page == "Donate Food":
        render_donation_form()
    elif page == "Register NGO":
        render_register_ngo()
    elif page == "NGO Directory":
        render_directory()
    elif page == "NGO Pickup":
        render_pickups()
    elif page == "Donation History":
        render_history()
    else:
        render_analytics()


main()
