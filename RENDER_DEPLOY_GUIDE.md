# Deploying Smart Shield to Render

Follow these step-by-step instructions to deploy the entire Smart Shield ecosystem (Database, Backend, and Frontend) to [Render](https://render.com/).

## Prerequisites
- A GitHub account with the project pushed to a repository.
- A Render account.

---

## Step 1: Managed PostgreSQL Database
Render's free tier for Web Services has ephemeral storage, so using local SQLite is not recommended. Use Render's managed PostgreSQL.

1.  Go to the [Render Dashboard](https://dashboard.render.com/).
2.  Click **New +** and select **PostgreSQL**.
3.  **Details**:
    *   **Name**: `smart-shield-db`
    *   **Database**: `smartshield`
    *   **User**: `admin`
    *   **Region**: Select the same region for all services (e.g., Oregon).
4.  Click **Create Database**.
5.  Once created, find the **Internal Database URL**. You will need this for the backend.

---

## Step 2: Backend Deployment (FastAPI)
1.  Click **New +** and select **Web Service**.
2.  Connect your GitHub repository.
3.  **Details**:
    *   **Name**: `smart-shield-api`
    *   **Root Directory**: `backend`
    *   **Runtime**: `Python 3`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
4.  **Environment Variables**:
    *   Click **Advanced** > **Add Environment Variable**.
    *   `DATABASE_URL`: Paste the **Internal Database URL** from Step 1.
    *   `JWT_SECRET_KEY`: Use a strong random string (e.g., `openssl rand -hex 32`).
    *   `ALLOWED_ORIGINS`: Set this to your frontend URL (you can update this after Step 3).
    *   `GOOGLE_MAPS_API_KEY`: (Optional) Your API key for routing.

---

## Step 3: Frontend Deployment (React)
1.  Click **New +** and select **Static Site**.
2.  Connect your GitHub repository.
3.  **Details**:
    *   **Name**: `smart-shield-app`
    *   **Root Directory**: `frontend`
    *   **Build Command**: `npm run build`
    *   **Publish Directory**: `build`
4.  **Environment Variables**:
    *   `REACT_APP_API_URL`: `https://smart-shield-api.onrender.com/api/v1` (Replace `smart-shield-api` with your actual service name).

---

## Step 4: Final Configuration
1.  Once the Frontend is deployed, you will get a URL (e.g., `https://smart-shield-app.onrender.com`).
2.  Go back to your **Backend Service** > **Environment**.
3.  Update `ALLOWED_ORIGINS` to include your React app URL.
4.  Restart the Backend service.

---

## Important Notes
- **Cold Starts**: Render's free tier spins down services after inactivity. The first request after a break may take 30-60 seconds.
- **Database Migrations**: The backend is configured to `init_db()` on startup, which will create the necessary Tables in your new PostgreSQL instance automatically.
- **CORS**: Ensure the trailing slash is handled correctly in your `REACT_APP_API_URL`.
