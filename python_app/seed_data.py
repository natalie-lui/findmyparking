
import os
from utils.supabase_client import get_supabase_client
import time

supabase = get_supabase_client()

spots = [
    # --- Structures (Major Hubs) ---
    {
        "name": "Anteater Parking Structure (APS)",
        "description": "Large structure near the ARC and engineering.",
        "location": "POINT(-117.8463 33.6425)",
        "cost_per_hour": 2.00,
        "capacity": 200,
        "availability_score": 0.8,
        "features": ["Covered", "EV Charging", "Handicap"]
    },
    {
        "name": "Social Science Parking Structure (SSPS)",
        "description": "Multi-level structure near Social Sciences and Student Center.",
        "location": "POINT(-117.8406 33.6455)",
        "cost_per_hour": 2.00,
        "capacity": 150,
        "availability_score": 0.6,
        "features": ["Covered", "Elevator"]
    },
    {
        "name": "Student Center Parking Structure (SCPS)",
        "description": "Prime location for Student Center and Pereira Drive.",
        "location": "POINT(-117.8466 33.6496)",
        "cost_per_hour": 3.00,
        "capacity": 300,
        "availability_score": 0.4,
        "features": ["Covered", "EV Charging", "Valet"]
    },
    {
        "name": "Mesa Parking Structure (MPS)",
        "description": "Located near Mesa Court housing and Arts.",
        "location": "POINT(-117.8540 33.6490)",
        "cost_per_hour": 2.00,
        "capacity": 250,
        "availability_score": 0.9,
        "features": ["Covered", "Accessible", "Bridge Access"]
    },
     {
        "name": "Division of Continuing Education (DCE) Structure",
        "description": "Structure serving the east side of campus.",
        "location": "POINT(-117.8380 33.6510)",
        "cost_per_hour": 2.00,
        "capacity": 180,
        "availability_score": 0.75,
        "features": ["Covered", "EV Charging"]
    },
    {
        "name": "East Campus Parking Structure (ECPS)",
        "description": "Newer structure serving Anteater Recreation Center & Bren.",
        "location": "POINT(-117.8285 33.6517)",
        "cost_per_hour": 1.50,
        "capacity": 400,
        "availability_score": 0.85,
        "features": ["Covered", "Modern", "Events"]
    },

    # --- Academic Lots (Zone 6, 3, etc.) ---
    {
        "name": "Jack Baskin/Engineering Lot",
        "description": "Open lot near Engineering Tower.",
        "location": "POINT(-117.8427 33.6427)",
        "cost_per_hour": 2.50,
        "capacity": 50,
        "availability_score": 0.3,
        "features": ["Open Air", "Quick Access"]
    },
    {
        "name": "Lot 16H (Biological Sciences)",
        "description": "Reserved and general parking near Bio Sci.",
        "location": "POINT(-117.8480 33.6400)",
        "cost_per_hour": 2.25,
        "capacity": 80,
        "availability_score": 0.7,
        "features": ["Open Air", "Handicap"]
    },
    {
        "name": "ARC Parking Lot",
        "description": "Large open lot for the Anteater Recreation Center.",
        "location": "POINT(-117.8490 33.6440)",
        "cost_per_hour": 1.50,
        "capacity": 120,
        "availability_score": 0.85,
        "features": ["Open Air", "Gym Access"]
    },
    {
        "name": "Gillespie Neuroscience Lot",
        "description": "Small lot near medical research buildings.",
        "location": "POINT(-117.8520 33.6410)",
        "cost_per_hour": 2.00,
        "capacity": 40,
        "availability_score": 0.5,
        "features": ["Open Air"]
    },
    {
        "name": "Lot 7 (Physical Sciences)",
        "description": "Close to Physical Sciences Lecture Hall.",
        "location": "POINT(-117.8450 33.6405)",
        "cost_per_hour": 2.00,
        "capacity": 60,
        "availability_score": 0.45,
        "features": ["Open Air"]
    },
    {
        "name": "Lot 12A (Ayala Science Library)",
        "description": "Closest open parking to Science Library.",
        "location": "POINT(-117.8495 33.6405)",
        "cost_per_hour": 2.00,
        "capacity": 100,
        "availability_score": 0.55,
        "features": ["Open Air"]
    },
    {
        "name": "Lot 12B (Steinhaus Hall)",
        "description": "Adjacent to Steinhaus Hall.",
        "location": "POINT(-117.8488 33.6412)",
        "cost_per_hour": 2.25,
        "capacity": 45,
        "availability_score": 0.4,
        "features": ["Open Air"]
    },
    {
        "name": "Lot 5 (Law School)",
        "description": "Near the School of Law.",
        "location": "POINT(-117.8415 33.6480)",
        "cost_per_hour": 2.00,
        "capacity": 90,
        "availability_score": 0.65,
        "features": ["Open Air"]
    },
    {
        "name": "CT Parking (Cyber A)",
        "description": "Small lot near Cyber buildings.",
        "location": "POINT(-117.8395 33.6430)",
        "cost_per_hour": 2.50,
        "capacity": 25,
        "availability_score": 0.35,
        "features": ["Open Air"]
    },
    
    # --- Housing & Remote Lots ---
    {
        "name": "Lot 1 (Mesa Court)",
        "description": "Small lot for dorm pick-up/drop-off.",
        "location": "POINT(-117.8530 33.6485)",
        "cost_per_hour": 2.50,
        "capacity": 30,
        "availability_score": 0.2,
        "features": ["Open Air", "Short Term"]
    },
    {
        "name": "Arroyo Vista Parking",
        "description": "Parking for AV Housing and ARC fields.",
        "location": "POINT(-117.8368 33.6552)",
        "cost_per_hour": 1.50,
        "capacity": 100,
        "availability_score": 0.8,
        "features": ["Open Air", "Housing"]
    },
    {
        "name": "Campus Village Parking",
        "description": "Parking for CV residents and Science Library overflow.",
        "location": "POINT(-117.8510 33.6482)",
        "cost_per_hour": 2.00,
        "capacity": 150,
        "availability_score": 0.6,
        "features": ["Open Air", "Housing"]
    },
    {
        "name": "Middle Earth Cluster",
        "description": "Near Ring Road and Middle Earth towers.",
        "location": "POINT(-117.8465 33.6468)",
        "cost_per_hour": 2.50,
        "capacity": 60,
        "availability_score": 0.3, # Always busy
        "features": ["Open Air", "Central"]
    },
    {
        "name": "Palo Verde Parking",
        "description": "Graduate housing parking.",
        "location": "POINT(-117.8596 33.6418)",
        "cost_per_hour": 1.50,
        "capacity": 200,
        "availability_score": 0.7,
        "features": ["Open Air", "Quiet"]
    },
    {
        "name": "Verano Place Parking",
        "description": "Graduate housing parking near Bio Sci.",
        "location": "POINT(-117.8637 33.6409)",
        "cost_per_hour": 1.50,
        "capacity": 250,
        "availability_score": 0.75,
        "features": ["Open Air", "Quiet"]
    },
    {
        "name": "Lot 70 (University Hills)",
        "description": "Remote lot for long term.",
        "location": "POINT(-117.8350 33.6400)",
        "cost_per_hour": 1.00,
        "capacity": 200,
        "availability_score": 0.95,
        "features": ["Open Air", "Cheap"]
    },
    {
        "name": "Lot 80 (East Campus)",
        "description": "Near Crawford Hall.",
        "location": "POINT(-117.8390 33.6495)",
        "cost_per_hour": 1.75,
        "capacity": 150,
        "availability_score": 0.8,
        "features": ["Open Air", "Sports"]
    },
    {
        "name": "Lot 30 (Tennis Courts)",
        "description": "Parking by the tennis courts.",
        "location": "POINT(-117.8510 33.6495)",
        "cost_per_hour": 2.00,
        "capacity": 70,
        "availability_score": 0.7,
        "features": ["Open Air"]
    },
    {
         "name": "Health Sciences Parking",
         "description": "Near Medical School entrance.",
         "location": "POINT(-117.8545 33.6400)",
         "cost_per_hour": 3.00,
         "capacity": 120,
         "availability_score": 0.5,
         "features": ["Covered", "Medical"]
    },
    {
         "name": "Vista del Campo Guest Lot",
         "description": "Visitor parking for VDC housing.",
         "location": "POINT(-117.8300 33.6450)",
         "cost_per_hour": 1.50,
         "capacity": 60,
         "availability_score": 0.9,
         "features": ["Open Air", "Remote"]
    }
]

def seed_database():
    print("Clearing existing parking spots...")
    try:
        supabase.table('parking_spots').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
    except Exception as e:
        print(f"Error clearing data (might be empty): {e}")

    print(f"Inserting {len(spots)} new spots...")
    try:
        data = supabase.table('parking_spots').insert(spots).execute()
        print("Success! Database seeded.")
        # print(data)
    except Exception as e:
        print(f"Error inserting data: {e}")

if __name__ == "__main__":
    seed_database()
