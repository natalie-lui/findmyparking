-- Enable PostGIS extension for geospatial queries
create extension if not exists postgis;

-- Users table (extends Supabase auth.users or standalone if not using Auth yet)
create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  email text unique,
  password text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  preferences jsonb default '{}'::jsonb -- e.g. { "max_cost": 10, "covered": true }
);

-- Parking Spots table
create table if not exists parking_spots (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  description text,
  location geography(Point) not null, -- PostGIS Point
  cost_per_hour float not null,
  capacity int not null,
  availability_score float default 0.5, -- 0.0 to 1.0 (Mock/Real-time)
  features jsonb default '[]'::jsonb, -- e.g. ["EV", "Covered", "Handicap", "Valet"]
  image_url text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Parking History table
create table if not exists parking_history (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  spot_name text not null,
  spot_lat double precision not null,
  spot_lon double precision not null,
  cost_per_hour float,
  walk_time_minutes float,
  parked_at timestamp with time zone default now()
);

-- Index for fast per-user history lookups
create index if not exists parking_history_user_id_index
  on parking_history (user_id);

-- Create a spatial index for fast distance queries
create index if not exists parking_spots_geo_index
  on parking_spots
  using GIST (location);

-- Function to find nearby spots within a radius (meters)
create or replace function nearby_spots(
  lat float,
  long float,
  radius_meters float
)
returns setof parking_spots
language sql
as $$
  select *
  from parking_spots
  where st_dwithin(
    location,
    st_point(long, lat)::geography,
    radius_meters
  );
$$;
