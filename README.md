# FindMyParking - Python/Streamlit Version

A personalized parking recommendation engine that uses real-time context (Weather, Traffic) and user preferences to suggest the best parking spots.

## Features
-   **Personalized Ranking**: Algorithm balances cost, distance, availability, and user preferences.
-   **Real-time Context**: Integrates OpenWeatherMap (Rain detection) and Mapbox (Traffic) to adjust recommendations dynamically.
-   **Interactive Map**: Visualizes user location and recommended spots using PyDeck.
-   **User Preferences**: Customize priorities (Max Cost, Covered Parking).

## Tech Stack
-   **Frontend**: Streamlit
-   **Backend/Logic**: Python
-   **Database**: Supabase (PostgreSQL + PostGIS).
-   **External APIs**: OpenWeatherMap, Mapbox Directions.

## Installation & Setup

### 1. Prerequisites
-   [Python 3.9+](https://www.python.org/downloads/)
-   [Git](https://git-scm.com/)

### 2. Clone and Install
```bash
git clone https://github.com/annahe04/findmyparking.git
cd findmyparking

# Create and activate virtual environment (Recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r python_app/requirements.txt
```

### 3. Environment Variables
Create a `.env.local` file in the root directory:
```bash
cp .env.local.example .env.local
```
Fill in the keys in `.env.local`:
-   `NEXT_PUBLIC_SUPABASE_URL`: Your Supabase Project URL.
-   `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Your Supabase Anon Public Key.
*(Note: Variable names kept compatible with previous setup)*
-   `OPENWEATHER_API_KEY`: (Optional) Free key from [OpenWeatherMap](https://openweathermap.org/).
-   `MAPBOX_ACCESS_TOKEN`: (Optional) Free token from [Mapbox](https://www.mapbox.com/).

### 4. Database Setup (Supabase)
If starting fresh:
1.  Create a new project at [supabase.com](https://supabase.com).
2.  Go to the **SQL Editor** (sidebar icon).
3.  Copy the contents of [`supabase/schema.sql`](supabase/schema.sql) and run it.
    *   This enables PostGIS and creates the `users` and `parking_spots` tables.

### 5. Run Application
Make sure your virtual environment is active:
```bash
source venv/bin/activate
streamlit run python_app/app.py
```
Open the URL shown in your terminal (usually [http://localhost:8501](http://localhost:8501)) to view the application.

## Troubleshooting
-   **ModuleNotFoundError**: Ensure you are running `streamlit` from inside your virtual environment. If using Anaconda, make sure `pip install` ran in the same environment as `streamlit`. Using the `venv` steps above avoids this.
