import { createClient } from '@supabase/supabase-js';
import { NextResponse } from 'next/server';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || '';

const supabase = createClient(supabaseUrl, supabaseServiceKey || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!);

const UCI_COORDS = { lat: 33.6405, lng: -117.8443 };

const MOCK_SPOTS = [
    {
        name: "Anteater Parking Structure",
        location: `POINT(${UCI_COORDS.lng - 0.002} ${UCI_COORDS.lat + 0.002})`,
        cost_per_hour: 2.0,
        capacity: 200,
        availability_score: 0.8,
        features: ["Covered", "EV Charging", "Handicap"],
        image_url: "https://images.unsplash.com/photo-1470224114660-3f6686c562eb?q=80&w=2535&auto=format&fit=crop"
    },
    {
        name: "Social Science Parking Structure",
        location: `POINT(${UCI_COORDS.lng + 0.003} ${UCI_COORDS.lat - 0.001})`,
        cost_per_hour: 2.5,
        capacity: 150,
        availability_score: 0.2,
        features: ["Covered", "Handicap"],
        image_url: "https://images.unsplash.com/photo-1573348722427-f1d6d19f49f8?q=80&w=2669&auto=format&fit=crop"
    },
    {
        name: "Mesa Parking Structure",
        location: `POINT(${UCI_COORDS.lng - 0.005} ${UCI_COORDS.lat - 0.003})`,
        cost_per_hour: 1.5,
        capacity: 300,
        availability_score: 0.9,
        features: ["Uncovered", "Cheapest"],
        image_url: "https://images.unsplash.com/photo-1590674899505-1c5c4195c60d?q=80&w=2574&auto=format&fit=crop"
    },
    {
        name: "Student Center Structure",
        location: `POINT(${UCI_COORDS.lng + 0.001} ${UCI_COORDS.lat + 0.004})`,
        cost_per_hour: 3.0,
        capacity: 100,
        availability_score: 0.1,
        features: ["Covered", "Valet", "EV Charging"],
        image_url: "https://images.unsplash.com/photo-1506521781263-d8422e82f27a?q=80&w=2670&auto=format&fit=crop"
    },
    {
        name: "Engineering Parking Lot",
        location: `POINT(${UCI_COORDS.lng + 0.004} ${UCI_COORDS.lat + 0.002})`,
        cost_per_hour: 2.0,
        capacity: 80,
        availability_score: 0.6,
        features: ["Uncovered"],
        image_url: "https://images.unsplash.com/photo-1542361345-89e58247f2d6?q=80&w=2670&auto=format&fit=crop"
    }
];

export async function GET() {
    try {



        const { data, error } = await supabase.from('parking_spots').insert(MOCK_SPOTS).select();

        if (error) {
            console.error("Error seeding data:", error);
            return NextResponse.json({ error: error.message }, { status: 500 });
        }

        return NextResponse.json({ message: "Seeding successful", data });
    } catch (err: any) {
        return NextResponse.json({ error: err.message }, { status: 500 });
    }
}
