# FindMyParking - Next Generation Parking Recommendation System

A personalized parking recommendation engine that uses real-time context (Weather, Traffic) and user preferences to suggest the best parking spots.

## Features
-   **Personalized Ranking**: Algorithm balances cost, distance, availability, and user preferences.
-   **Real-time Context**: Integrates OpenWeatherMap (Rain detection) and Mapbox (Traffic) to adjust recommendations dynamically.
-   **Interactive Map**: Visualizes user location and recommended spots.
-   **User Preferences**: Customize priorities (Max Cost, Covered Parking).

## Tech Stack
-   **Frontend**: Next.js 14+ (App Router), TailwindCSS, Leaflet.
-   **Backend**: Next.js API Routes.
-   **Database**: Supabase (PostgreSQL + PostGIS).
-   **External APIs**: OpenWeatherMap, Mapbox Directions.

## Setup Instructions

### 1. Environment Variables
Rename `.env.local.example` to `.env.local` and fill in your keys:
```bash
cp .env.local.example .env.local
```
You will need:
-   `NEXT_PUBLIC_SUPABASE_URL` & `NEXT_PUBLIC_SUPABASE_ANON_KEY` (from Supabase Dashboard)
-   `OPENWEATHER_API_KEY` (optional, falls back to mock)
-   `MAPBOX_ACCESS_TOKEN` (optional, falls back to mock)

### 2. Database Setup (Supabase)
Run the SQL found in [`supabase/schema.sql`](supabase/schema.sql) in your Supabase SQL Editor.
This will create the `parking_spots` table and `nearby_spots` function.

### 3. Seed Data
After setting up the database and environment variables, run the seed script by visiting the API route in your browser or via curl:
```bash
curl http://localhost:3000/api/seed
```
This will populate the database with mock parking spots around UCI.

### 4. Run Development Server
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to view the application.

## Testing Scenarios
1.  **Rainy Day**: Changes recommendations to favor covered parking (simulated if no API key or actual rain).
2.  **Budget User**: Set "Max Cost" low in settings -> Cheap spots ranked higher.
