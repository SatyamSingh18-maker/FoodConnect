# Streamlit Deployment

FoodConnect now has a Streamlit frontend in `streamlit_frontend.py`. The Flask API must be hosted separately; Streamlit Community Cloud does not run `app.py` as a second web service.

## Run Locally

Install dependencies, start the Flask API in one terminal, and start Streamlit in another:

```powershell
pip install -r requirements.txt
python app.py
streamlit run streamlit_frontend.py
```

The local Streamlit app uses `http://127.0.0.1:5000` by default.

## Deploy the API

Host the Flask API on a Python web service with a persistent PostgreSQL database. For example, a Render web service can use:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
- Environment variable: `DATABASE_URL` set to the managed PostgreSQL connection string

The backend converts `postgres://` and `postgresql://` URLs to the psycopg 3 SQLAlchemy driver format. Keep the database persistent; the default SQLite database is intended only for local development.

## Deploy the Streamlit Frontend

1. Push the repository to a GitHub account connected to Streamlit Community Cloud.
2. Create a Streamlit app from that repository and set **Main file path** to `streamlit_frontend.py`.
3. Add this secret in the Streamlit app settings, replacing the value with the deployed Flask API origin:

```toml
FOODCONNECT_API_URL = "https://your-foodconnect-api.example.com"
```

4. Deploy the app. Streamlit installs the Python dependencies from `requirements.txt`.

Pickup QR scanning uses a browser camera capture and requires HTTPS on the deployed site. Manual token entry remains available as a fallback.

## Before Public Production

The current API has no authentication or role-based access control, permits public NGO registration and exposes donor contact data in donation responses. Do not use it with public real-world donor data until authentication, authorization, and data minimization are implemented. The deployment configuration here makes the app hostable; it does not make the API production-secure.
