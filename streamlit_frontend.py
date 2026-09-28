import os
from datetime import date, datetime, time, timedelta, timezone
from io import BytesIO
from zoneinfo import ZoneInfo

import qrcode
import streamlit as st

from app import app as flask_app


# Direct Flask connection
flask_client = flask_app.test_client()


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


st.set_page_config(
    page_title="FoodConnect",
    page_icon="🥬",
    layout="wide"
)


st.html(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800;900&display=swap');

        :root {
            color-scheme: dark !important;
            --primary-color: #0066CC !important;
            --background-color: #121212 !important;
            --secondary-background-color: #1E1E1E !important;
            --text-color: #FFFFFF !important;
        }

        html, body, [class*="css"] {
            font-family: 'Archivo', sans-serif;
        }

        .stApp, [data-testid="stAppViewContainer"] {
            background: #121212 !important;
            color: #FFFFFF !important;
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 1380px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        [data-testid="stSidebar"] {
            background: #171717 !important;
            border-right: 1px solid #303030;
        }

        [data-testid="stHeader"] {
            background: #121212 !important;
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.4rem;
        }

        h1, h2, h3, h4, p, label {
            color: #FFFFFF;
        }

        h1 {
            font-size: clamp(2.25rem, 4vw, 3.6rem);
            line-height: 1;
        }

        h2 {
            font-size: 1.55rem;
        }

        .brand-lockup {
            color: #FFFFFF;
            font-size: 1.15rem;
            font-weight: 900;
            letter-spacing: .02em;
        }

        .brand-lockup span {
            color: #0066CC;
        }

        .eyebrow {
            color: #0066CC;
            font-size: .69rem;
            font-weight: 800;
            letter-spacing: .14em;
            text-transform: uppercase;
            margin: 0 0 .8rem;
        }

        .lead {
            color: #C8C8C8;
            font-size: 1.05rem;
            line-height: 1.65;
            max-width: 780px;
        }

        .page-hero {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 2rem;
            padding: clamp(1.5rem, 4vw, 3.2rem);
            margin-bottom: 1.6rem;
            border: 1px solid #303030;
            border-left: 5px solid #0066CC;
            border-radius: 8px;
            background: #1B1B1B;
            position: relative;
            overflow: hidden;
        }

        .page-hero:after {
            content: '';
            position: absolute;
            inset: 0 0 0 auto;
            width: 30%;
            opacity: .18;
            background: repeating-linear-gradient(
                135deg,
                transparent 0 18px,
                #0066CC 19px 20px,
                transparent 21px 38px
            );
            pointer-events: none;
        }

        .page-hero-copy {
            position: relative;
            z-index: 1;
            max-width: 800px;
        }

        .page-hero h1 {
            margin: 0 0 .85rem;
        }

        .page-hero p:not(.eyebrow) {
            color: #C8C8C8;
            font-size: 1rem;
            line-height: 1.6;
            max-width: 740px;
            margin: 0;
        }

        .hero-mark {
            position: relative;
            z-index: 1;
            flex: none;
            width: 78px;
            height: 78px;
            display: grid;
            place-items: center;
            border-radius: 8px;
            background: #0066CC;
            color: #FFFFFF;
            font-size: 2.2rem;
            font-weight: 900;
        }

        .section-kicker {
            color: #0066CC;
            font-size: .68rem;
            font-weight: 800;
            letter-spacing: .12em;
            text-transform: uppercase;
            margin: 1.3rem 0 .65rem;
        }

        .surface {
            border: 1px solid #303030;
            border-radius: 8px;
            padding: 1.15rem 1.3rem;
            background: #1B1B1B;
            margin: .4rem 0 1rem;
        }

        .muted {
            color: #B5B5B5;
            font-size: .9rem;
        }

        .status {
            display: inline-block;
            padding: .25rem .55rem;
            border-radius: 4px;
            font-size: .69rem;
            font-weight: 800;
            text-transform: uppercase;
        }

        .status-open {
            background: #173A28;
            color: #9EE3B5;
        }

        .status-accepted {
            background: #142D48;
            color: #9BC9FF;
        }

        .status-completed {
            background: #12382F;
            color: #91E0CA;
        }

        .status-expired {
            background: #45201F;
            color: #FFB4AE;
        }

        div.stButton > button[kind="primary"],
        button[kind="primaryFormSubmit"] {
            background: #0066CC;
            color: #FFFFFF;
            border: 0;
            font-weight: 700;
        }

        div.stButton > button {
            border-radius: 7px;
            min-height: 2.6rem;
        }

        div.stButton > button[kind="primary"]:hover {
            background: #0057AD;
            border-color: #0057AD;
            color: #FFFFFF;
        }

        [data-testid="stMetric"] {
            border: 1px solid #303030;
            border-top: 3px solid #0066CC;
            background: #1B1B1B;
            padding: 1rem 1.1rem;
            border-radius: 8px;
        }

        [data-testid="stMetricValue"] {
            color: #FFFFFF;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: #1B1B1B;
            border-color: #303030;
            border-radius: 8px;
        }

        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stDateInput"] input,
        [data-testid="stTimeInput"] input,
        [data-testid="stSelectbox"] > div > div {
            border-radius: 6px;
        }

        [data-testid="stRadio"] label {
            font-weight: 600;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label {
            padding: .32rem .5rem;
            border-radius: 5px;
            color: #E5E5E5;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
            background: #142D48;
            color: #A9D1FF;
        }

        [data-testid="stForm"] {
            background: #1B1B1B;
            border: 1px solid #303030;
            border-radius: 8px;
            padding: 1.2rem 1.35rem;
        }

        [data-testid="stAlert"] {
            border-radius: 7px;
        }

        @media (max-width: 700px) {
            .page-hero {
                padding: 1.35rem;
            }

            .hero-mark {
                width: 54px;
                height: 54px;
                font-size: 1.5rem;
            }
        }
    </style>
    """,
)


def render_page_hero(eyebrow, title, subtitle, mark="F"):
    st.markdown(
        f'<section class="page-hero">'
        f'<div class="page-hero-copy">'
        f'<p class="eyebrow">{eyebrow}</p>'
        f'<h1>{title}</h1>'
        f'<p>{subtitle}</p>'
        f'</div>'
        f'<div class="hero-mark">{mark}</div>'
        f'</section>',
        unsafe_allow_html=True,
    )


# ============================================================
# API CONNECTION
# ============================================================

def api_request(method, path, **kwargs):
    try:
        response = flask_client.open(
            path,
            method=method,
            json=kwargs.get("json"),
        )

    except Exception as exc:
        return None, f"FoodConnect service is unavailable: {exc}"

    try:
        payload = response.get_json(silent=True)
    except Exception:
        payload = {}

    if payload is None:
        payload = {}

    # FIX:
    # WrapperTestResponse does not have response.ok.
    # Flask test client uses status_code.
    if response.status_code < 200 or response.status_code >= 300:
        return None, payload.get(
            "error",
            f"API request failed ({response.status_code})."
        )

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

    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if image is None:
        return ""

    decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(image)

    return decoded.strip()


def utc_iso(day_value, time_value, zone_name):
    local_value = datetime.combine(
        day_value,
        time_value
    ).replace(
        tzinfo=ZoneInfo(zone_name)
    )

    return local_value.astimezone(timezone.utc).isoformat()


def render_about():

    render_page_hero(
        "About FoodConnect",
        "Good food deserves a better destination.",
        "We connect surplus food with nearby NGOs so useful meals reach communities instead of going to waste.",
    )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Our purpose")
        st.write(
            "Turn surplus into shared value. Donors can offer food "
            "to local organizations that can collect and distribute it."
        )

    with right:
        st.subheader("How we help")
        st.write(
            "Location-based matching, clear donation statuses, "
            "and QR-verified collection make handoffs easier to coordinate."
        )

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric("Local matching", "Nearby NGOs")
    c2.metric("Verified handoffs", "QR pickup")
    c3.metric("Shared outcome", "Less food waste")

    return st.button(
        "Explore FoodConnect",
        type="primary"
    )


def render_home(navigate):

    render_page_hero(
        "Surplus food rescue platform",
        "Good food. Less waste. More hope.",
        "Connect surplus food with NGOs. FoodConnect makes rescue and pickup traceable and reliable.",
        "↗",
    )

    total_col, open_col, accepted_col, completed_col = st.columns(4)

    analytics, error = get_api("/api/analytics")

    if error:
        show_error(error)
    else:
        total_col.metric(
            "Donations",
            analytics["total_donations"]
        )
        open_col.metric(
            "Open",
            analytics["open"]
        )
        accepted_col.metric(
            "Accepted",
            analytics["accepted"]
        )
        completed_col.metric(
            "Completed",
            analytics["completed"]
        )

    st.divider()

    st.markdown(
        '<p class="section-kicker">Choose where to begin</p>',
        unsafe_allow_html=True
    )

    cols = st.columns(3)

    for col, page, title, copy in zip(
        cols,
        ["Donate Food", "NGO Pickup", "Analytics"],
        ["Share surplus food", "Coordinate a pickup", "See the impact"],
        [
            "Post a pickup-ready donation.",
            "Accept and verify collection.",
            "Review live donation activity."
        ],
    ):
        with col:
            st.markdown(
                f'<div class="surface">'
                f'<h3>{title}</h3>'
                f'<p class="muted">{copy}</p>'
                f'</div>',
                unsafe_allow_html=True
            )

            if st.button(
                f"Open {page}",
                key=f"home-{page}"
            ):
                navigate(page)


def render_donation_form():

    render_page_hero(
        "Donate surplus",
        "Share food. Start a rescue.",
        "Tell us what is available and where it can be collected. Nearby NGOs are matched after posting.",
        "+",
    )

    if "last_donation" not in st.session_state:
        st.session_state.last_donation = None

    with st.form("donation-form"):

        donor_col, phone_col = st.columns(2)

        donor_name = donor_col.text_input(
            "Donor name",
            max_chars=120
        )

        donor_phone = phone_col.text_input(
            "Phone number",
            max_chars=20
        )

        location = st.text_input(
            "Pickup address",
            max_chars=255
        )

        latitude_col, longitude_col = st.columns(2)

        latitude = latitude_col.number_input(
            "Latitude",
            min_value=-90.0,
            max_value=90.0,
            value=19.0760,
            format="%.6f"
        )

        longitude = longitude_col.number_input(
            "Longitude",
            min_value=-180.0,
            max_value=180.0,
            value=72.8777,
            format="%.6f"
        )

        food_col, quantity_col = st.columns(2)

        food_type = food_col.selectbox(
            "Food type",
            ["veg", "non-veg"],
            format_func=lambda value:
                "Vegetarian"
                if value == "veg"
                else "Non-vegetarian"
        )

        quantity = quantity_col.text_input(
            "Quantity",
            placeholder="e.g. 20 meal portions",
            max_chars=120
        )

        zone_name = st.selectbox(
            "Time zone",
            ["Asia/Kolkata", "UTC"]
        )

        now_local = datetime.now(
            ZoneInfo(zone_name)
        )

        cooked_date_col, cooked_time_col = st.columns(2)

        cooked_date = cooked_date_col.date_input(
            "Prepared date",
            value=now_local.date()
        )

        cooked_time = cooked_time_col.time_input(
            "Prepared time",
            value=now_local.time().replace(
                tzinfo=None,
                second=0,
                microsecond=0
            )
        )

        deadline_date_col, deadline_time_col = st.columns(2)

        deadline_date = deadline_date_col.date_input(
            "Pickup deadline date",
            value=(now_local + timedelta(hours=4)).date()
        )

        deadline_time = deadline_time_col.time_input(
            "Pickup deadline time",
            value=(now_local + timedelta(hours=4)).time().replace(
                tzinfo=None,
                second=0,
                microsecond=0
            )
        )

        notes = st.text_area(
            "Additional notes (optional)",
            max_chars=2000
        )

        submitted = st.form_submit_button(
            "Post donation",
            type="primary",
            use_container_width=True
        )

    if submitted:

        if not all([
            donor_name.strip(),
            donor_phone.strip(),
            location.strip(),
            quantity.strip()
        ]):
            st.error(
                "Fill in the donor, contact, address, and quantity fields."
            )
        else:

            payload = {
                "donor_name": donor_name.strip(),
                "donor_phone": donor_phone.strip(),
                "location_text": location.strip(),
                "lat": latitude,
                "lng": longitude,
                "food_type": food_type,
                "quantity_desc": quantity.strip(),
                "cooked_time": utc_iso(
                    cooked_date,
                    cooked_time,
                    zone_name
                ),
                "pickup_deadline": utc_iso(
                    deadline_date,
                    deadline_time,
                    zone_name
                ),
                "notes": notes.strip(),
            }

            result, error = post_api(
                "/api/donations",
                payload
            )

            if error:
                st.error(error)
            else:

                st.session_state.last_donation = result

                st.success(
                    f"Donation #{result['donation']['id']} "
                    "posted and open for pickup."
                )

    result = st.session_state.last_donation

    if result:

        donation = result["donation"]

        st.divider()

        st.subheader(
            f"Donation #{donation['id']} · Pickup credentials"
        )

        qr_col, detail_col = st.columns([1, 2])

        with qr_col:
            st.image(
                qr_image(donation["qr_token"]),
                width=190
            )

        with detail_col:

            st.code(
                donation["qr_token"],
                language=None
            )

            st.caption(
                "Show this QR or share the token with the accepting NGO."
            )

            matches = result.get(
                "notify",
                []
            )

            st.markdown(
                "**Nearby NGO matches**"
            )

            if matches:

                for match in matches:
                    st.write(
                        f"{match['ngo']['name']} · "
                        f"{match['distance_km']:.1f} km"
                    )

            else:
                st.info(
                    "No nearby NGOs matched yet."
                )


def render_register_ngo():

    render_page_hero(
        "Join the rescue network",
        "Register your NGO.",
        "Share your organization’s location and pickup capacity so donors can find you.",
        "N",
    )

    with st.form("ngo-registration"):

        name_col, phone_col = st.columns(2)

        name = name_col.text_input(
            "Organization name",
            max_chars=120
        )

        phone = phone_col.text_input(
            "Contact phone",
            max_chars=20
        )

        lat_col, lng_col = st.columns(2)

        lat = lat_col.number_input(
            "Latitude",
            min_value=-90.0,
            max_value=90.0,
            value=19.0760,
            format="%.6f"
        )

        lng = lng_col.number_input(
            "Longitude",
            min_value=-180.0,
            max_value=180.0,
            value=72.8777,
            format="%.6f"
        )

        capacity_col, response_col = st.columns(2)

        capacity = capacity_col.number_input(
            "Pickup capacity",
            min_value=0,
            value=100,
            step=1
        )

        response_minutes = response_col.number_input(
            "Average response time (minutes)",
            min_value=0,
            value=20,
            step=1
        )

        vehicle = st.checkbox(
            "Pickup vehicle available",
            value=True
        )

        submitted = st.form_submit_button(
            "Register organization",
            type="primary"
        )

    if submitted:

        payload = {
            "name": name.strip(),
            "phone": phone.strip(),
            "lat": lat,
            "lng": lng,
            "capacity": capacity,
            "avg_response_minutes": response_minutes,
            "vehicle_available": vehicle,
        }

        if not payload["name"] or not payload["phone"]:

            st.error(
                "Organization name and contact phone are required."
            )

            return

        result, error = post_api(
            "/api/ngos",
            payload
        )

        if error:
            st.error(error)
        else:

            verification = (
                "verified"
                if result["verified"]
                else "pending review"
            )

            st.success(
                f"{result['name']} registered; "
                f"status is {verification}."
            )


def render_directory():

    render_page_hero(
        "Community partners",
        "NGO Directory",
        "Find local organizations ready to collect and distribute surplus food.",
        "◎",
    )

    ngos, error = get_api(
        "/api/ngos"
    )

    if error:
        show_error(error)
        return

    query = st.text_input(
        "Search organizations",
        placeholder="Search by NGO name"
    )

    matches = [
        ngo
        for ngo in ngos
        if query.casefold()
        in ngo["name"].casefold()
    ]

    if not matches:

        st.info(
            "No organizations match that search."
            if ngos
            else
            "No NGOs are registered yet."
        )

        return

    columns = st.columns(2)

    for index, ngo in enumerate(matches):

        with columns[index % 2]:

            with st.container(border=True):

                status = (
                    "Verified"
                    if ngo["verified"]
                    else "Pending review"
                )

                st.subheader(
                    ngo["name"]
                )

                st.caption(
                    f"{status} · {ngo['phone']}"
                )

                st.write(
                    f"Coordinates: "
                    f"{ngo['lat']:.4f}, "
                    f"{ngo['lng']:.4f}"
                )

                st.write(
                    f"Capacity: {ngo['capacity']} · "
                    f"Response: {ngo['avg_response_minutes']} min"
                )

                st.write(
                    "Vehicle available"
                    if ngo["vehicle_available"]
                    else
                    "No vehicle listed"
                )

                st.link_button(
                    "Open map",
                    f"https://www.google.com/maps?"
                    f"q={ngo['lat']},{ngo['lng']}"
                )


def render_pickups():

    render_page_hero(
        "NGO operations",
        "Pickups in motion.",
        "Accept available donations and verify collection with the donor’s pickup token.",
        "↗",
    )

    ngos, ngo_error = get_api(
        "/api/ngos"
    )

    donations, donation_error = get_api(
        "/api/donations"
    )

    if ngo_error or donation_error:

        show_error(
            ngo_error or donation_error
        )

        return

    if not ngos:

        st.info(
            "Register an NGO before accepting pickup requests."
        )

        return

    ngo_by_id = {
        ngo["id"]: ngo
        for ngo in ngos
    }

    selected_id = st.selectbox(
        "Operating NGO",
        options=list(ngo_by_id),
        format_func=lambda ngo_id:
            ngo_by_id[ngo_id]["name"]
            +
            (
                " · Verified"
                if ngo_by_id[ngo_id]["verified"]
                else ""
            ),
    )

    counts = {
        status:
        sum(
            item["status"] == status
            for item in donations
        )
        for status in STATUS_OPTIONS[1:]
    }

    filter_status = st.radio(
        "Filter donations",
        STATUS_OPTIONS,
        format_func=lambda value:
            "All"
            if value == "all"
            else
            f"{STATUS_LABELS[value]} ({counts[value]})",
        horizontal=True,
    )

    visible = [
        item
        for item in donations
        if filter_status == "all"
        or item["status"] == filter_status
    ]

    if not visible:

        st.info(
            "No donations in this status yet."
        )

        return

    for donation in visible:

        with st.container(border=True):

            header_col, status_col = st.columns(
                [4, 1]
            )

            header_col.subheader(
                donation["quantity_desc"]
            )

            status_col.markdown(
                f'<span class="status '
                f'status-{donation["status"]}">'
                f'{donation["status"]}'
                f'</span>',
                unsafe_allow_html=True
            )

            st.write(
                f"{donation['food_type'].replace('-', ' ').title()} "
                f"· Donated by {donation['donor_name']}"
            )

            st.write(
                f"Pickup: {donation['location_text']}"
            )

            st.caption(
                f"Pickup before "
                f"{donation['pickup_deadline']}"
            )

            if donation.get(
                "accepted_by_ngo_name"
            ):

                st.info(
                    f"Accepted by "
                    f"{donation['accepted_by_ngo_name']}"
                )

            if donation["status"] == "open":

                if st.button(
                    "Accept pickup",
                    key=f"accept-{donation['id']}",
                    type="primary"
                ):

                    result, error = post_api(
                        f"/api/donations/"
                        f"{donation['id']}/accept",
                        {
                            "ngo_id": selected_id
                        },
                    )

                    if error:
                        st.error(error)
                    else:

                        st.success(
                            f"Donation #{donation['id']} "
                            f"accepted by "
                            f"{result.get('accepted_by_ngo_name', ngo_by_id[selected_id]['name'])}."
                        )

                        st.rerun()

            elif donation["status"] == "accepted":

                credential_col, confirm_col = st.columns(
                    [1, 2]
                )

                with credential_col:

                    st.image(
                        qr_image(donation["qr_token"]),
                        width=170
                    )

                with confirm_col:

                    st.markdown(
                        f"**Accepted by "
                        f"{donation.get('accepted_by_ngo_name') or 'NGO'}**"
                    )

                    st.code(
                        donation["qr_token"],
                        language=None
                    )

                    token_key = (
                        f"token-{donation['id']}"
                    )

                    captured_qr = st.camera_input(
                        "Scan pickup QR",
                        key=f"camera-{donation['id']}"
                    )

                    if captured_qr:

                        try:

                            decoded_token = decode_qr_image(
                                captured_qr.getvalue()
                            )

                            if decoded_token:

                                st.session_state[
                                    token_key
                                ] = decoded_token

                                st.success(
                                    "QR token scanned."
                                )

                            else:

                                st.warning(
                                    "No QR token was detected. "
                                    "Try again or enter the token manually."
                                )

                        except ImportError:

                            st.warning(
                                "Camera QR scanning is unavailable; "
                                "enter the token manually."
                            )

                    token = st.text_input(
                        "Pickup token",
                        key=token_key,
                        placeholder="Scan QR or enter token"
                    )

                    if st.button(
                        "Confirm pickup",
                        key=f"confirm-{donation['id']}",
                        type="primary"
                    ):

                        result, error = post_api(
                            f"/api/donations/"
                            f"{donation['id']}/confirm-pickup",
                            {
                                "qr_token": token.strip()
                            },
                        )

                        if error:
                            st.error(error)
                        else:

                            st.success(
                                f"Pickup #{donation['id']} completed."
                            )

                            st.rerun()

            elif donation["status"] == "expired":

                st.warning(
                    "Pickup deadline passed before collection. "
                    "This donation can no longer be accepted or confirmed."
                )


def render_history():

    render_page_hero(
        "Traceable food rescue",
        "Donation History",
        "Follow every donation from posting through acceptance, pickup, or expiry.",
        "↻",
    )

    donations, error = get_api(
        "/api/donations"
    )

    if error:
        show_error(error)
        return

    status = st.selectbox(
        "Status",
        STATUS_OPTIONS,
        format_func=lambda value:
            "All"
            if value == "all"
            else
            STATUS_LABELS[value]
    )

    visible = [
        donation
        for donation in donations
        if status == "all"
        or donation["status"] == status
    ]

    st.caption(
        f"{len(visible)} donation records"
    )

    for donation in visible:

        with st.container(border=True):

            cols = st.columns(
                [3, 1]
            )

            cols[0].subheader(
                donation["quantity_desc"]
            )

            cols[1].markdown(
                f'<span class="status '
                f'status-{donation["status"]}">'
                f'{donation["status"]}'
                f'</span>',
                unsafe_allow_html=True
            )

            st.write(
                f"{donation['food_type'].replace('-', ' ').title()} "
                f"· {donation['donor_name']}"
            )

            st.write(
                donation["location_text"]
            )

            st.caption(
                f"Posted {donation['created_at']} · "
                f"Pickup deadline {donation['pickup_deadline']}"
            )

            if donation.get(
                "accepted_by_ngo_name"
            ):

                st.caption(
                    f"Accepted by "
                    f"{donation['accepted_by_ngo_name']}"
                )

            if donation["status"] == "expired":

                st.warning(
                    "Pickup deadline passed before collection."
                )


def render_analytics():

    render_page_hero(
        "Live reporting",
        "Rescue impact, in view.",
        "Track donation activity and pickup outcomes from the FoodConnect database.",
        "%",
    )

    analytics, error = get_api(
        "/api/analytics"
    )

    if error:

        show_error(error)

        return

    columns = st.columns(5)

    columns[0].metric(
        "Total donations",
        analytics["total_donations"]
    )

    columns[1].metric(
        "Open",
        analytics["open"]
    )

    columns[2].metric(
        "Accepted",
        analytics["accepted"]
    )

    columns[3].metric(
        "Completed",
        analytics["completed"]
    )

    columns[4].metric(
        "Expired",
        analytics.get("expired", 0)
    )

    st.subheader(
        "Donation status"
    )

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

    completed_rate = (
        round(
            analytics["completed"]
            / total
            * 100
        )
        if total
        else 0
    )

    st.metric(
        "Completion rate",
        f"{completed_rate}%"
    )


def main():

    requested_page = st.query_params.get(
        "page",
        "About Us"
    )

    if requested_page in PAGES:
        st.session_state["page_nav"] = requested_page

    def sync_navigation():
        st.query_params["page"] = (
            st.session_state["page_nav"]
        )

    def navigate(target):
        st.query_params["page"] = target
        st.rerun()

    with st.sidebar:

        st.markdown(
            "## 🥬 FoodConnect"
        )

        st.caption(
            "Good food · Less waste · More hope"
        )

        page = st.radio(
            "Navigate",
            PAGES,
            key="page_nav",
            on_change=sync_navigation,
            label_visibility="collapsed"
        )

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


if __name__ == "__main__":
    main()
    