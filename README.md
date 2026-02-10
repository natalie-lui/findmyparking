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

## Installation & Setup

### 1. Prerequisites
-   [Node.js](https://nodejs.org/) (v18 or higher)
-   [Git](https://git-scm.com/)

### 2. Clone and Install
```bash
git clone https://github.com/annahe04/findmyparking.git
cd findmyparking
npm install
```

### 3. Environment Variables
Create a `.env.local` file in the root directory:
```bash
cp .env.local.example .env.local
```
Fill in the keys in `.env.local`:
-   `NEXT_PUBLIC_SUPABASE_URL`: Your Supabase Project URL.
-   `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Your Supabase Anon Public Key.
-   `OPENWEATHER_API_KEY`: (Optional) Free key from [OpenWeatherMap](https://openweathermap.org/).
-   `MAPBOX_ACCESS_TOKEN`: (Optional) Free token from [Mapbox](https://www.mapbox.com/).

### 4. Database Setup (Supabase)
1.  Create a new project at [supabase.com](https://supabase.com).
2.  Go to the **SQL Editor** (sidebar icon).
3.  Copy the contents of [`supabase/schema.sql`](supabase/schema.sql) and run it.
    *   This enables PostGIS and creates the `users` and `parking_spots` tables.

### 5. Seed Data
Populate the database with mock parking spots around UCI:
1.  Start the server: `npm run dev`
2.  Visit this URL in your browser: [http://localhost:3000/api/seed](http://localhost:3000/api/seed)
    *   You should see `{"message": "Seeding successful", ...}`.

### 6. Run Application
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to view the application.

## Usage Scenarios to Try
1.  **Simulate Rain**: In `src/lib/weather.ts`, force `return { condition: 'Rain', ... }`. Covered spots will rank higher.
2.  **Budget User**: Click the Settings (gear icon), set "Max Cost" to $1.50. Cheaper spots will rank #1.
3.  **Traffic**: Use Mapbox keys to see traffic-weighted ranking (spots closer in *time* rank higher).
