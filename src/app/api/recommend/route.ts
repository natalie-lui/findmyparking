import { createClient } from '@supabase/supabase-js';
import { NextRequest, NextResponse } from 'next/server';
import { getWeather } from '@/lib/weather';
import { getTravelTime } from '@/lib/traffic';

// Initialize Supabase Client
const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export async function POST(req: NextRequest) {
    try {
        const body = await req.json();
        const { lat, lng, preferences } = body;
        // preferences: { maxCost, maxDistance, covered, accessible }

        if (!lat || !lng) {
            return NextResponse.json({ error: "Location (lat, lng) is required" }, { status: 400 });
        }

        // 1. Fetch Real-time Context (Weather)
        const weather = await getWeather(lat, lng);
        const isRaining = weather?.isRaining || false;
        const isHot = (weather?.temp || 0) > 30;

        // 2. Fetch Candidate Spots (simple radius search)
        // Using RPC if available, or standard select if not. 
        // For this mock, standard select on small DB is fine, but let's try RPC as defined in schema.
        // If RPC fails (not created), fallback to JS filtering (for the demo stability).

        let spots: any[] = [];

        const { data: rpcData, error: rpcError } = await supabase
            .rpc('nearby_spots', { lat, long: lng, radius_meters: preferences?.maxDistance || 2000 });

        if (!rpcError && rpcData) {
            spots = rpcData;
        } else {
            // Fallback: fetch all and filter (ONLY for small mock dataset)
            const { data: allSpots } = await supabase.from('parking_spots').select('*');
            spots = allSpots || [];
            // Simple Haversine filtering would go here if we were strict, but let's just use all for ranking demo
        }

        // 3. Rank Spots
        const rankedSpots = await Promise.all(spots.map(async (spot) => {
            let score = 0;
            let reasons: string[] = [];

            // --- Distance & Traffic ---
            // We assume user is driving TO the spot.
            // We can fetch traffic from User(lat/lng) -> Spot(location).
            // Parse Point(x y) or use stored lat/long if we had it separately. 
            // PostGIS points are usually binary in Supabase JS unless cast. 
            // The seed script used WKT. Let's assume we can get lat/long from the 'location' column if we select it as text, 
            // or we just use a helper if we stored separate columns. 
            // For this demo, let's roughly parse the location string or just use Euclidean if complex.
            // *Correction*: usage of 'nearby_spots' returns what the table has.
            // Let's assume we can extract coords. For mock data, let's just trust the distance calc from PostGIS if we used it, 
            // or re-calculate roughly.

            // Let's assume spot.location is returned as GeoJSON or WKT. 
            // Actually, standard supabase select on geography returns GeoJSON object or string.
            // We will skip precise traffic API calls for *every* spot to avoid rate limits/latency in this loop 
            // unless we limit candidates. Let's limit to top 5 candidates by raw distance first?
            // For the demo, let's simulate traffic based on generic "distance" and random factor if API not called.

            // MOCK TRAFFIC CALL (or real if enabled)
            // Extract lat/long from WKT "POINT(lng lat)"
            let spotLat = lat;
            let spotLng = lng;
            // Primitive parsing for demo resilience
            if (typeof spot.location === 'string' && spot.location.startsWith('POINT')) {
                const parts = spot.location.replace('POINT(', '').replace(')', '').split(' ');
                spotLng = parseFloat(parts[0]);
                spotLat = parseFloat(parts[1]);
            }

            const traffic = await getTravelTime(lat, lng, spotLat, spotLng);
            const travelTime = traffic?.duration || 0; // seconds
            const isTrafficHeavy = traffic?.trafficCongestion === 'heavy' || traffic?.trafficCongestion === 'severe';

            // --- SCORING (Lower is better, or Higher is better? Let's use 0-100 Score where Higher is Better) ---
            // Start with Base 100
            score = 70; // Start neutral

            // 1. Distance/Time Penalty
            // -1 point per minute of travel
            const travelMinutes = travelTime / 60;
            score -= travelMinutes * 2;
            if (travelMinutes < 5) score += 10; // Bonus for very close

            if (isTrafficHeavy) {
                score -= 15;
                reasons.push("Heavy traffic on route");
            }

            // 2. Cost Penalty
            // -2 points per dollar
            score -= spot.cost_per_hour * 2;
            if (spot.cost_per_hour < 3) {
                score += 5; // Cheap bonus
                reasons.push("Low cost");
            }

            // 3. User Preferences & Weather
            const features = spot.features || [];
            const isCovered = features.includes("Covered");
            const isUncovered = features.includes("Uncovered"); // or just !Covered

            if (isRaining) {
                if (isCovered) {
                    score += 30; // HUGE bonus
                    reasons.push("Covered parking (Good for Rain)");
                } else {
                    score -= 20; // Penalty
                    reasons.push("Uncovered during rain");
                }
            }

            // Explicit Preferences
            if (preferences?.covered && isCovered) {
                score += 15;
                reasons.push("Matches 'Covered' preference");
            }
            if (preferences?.maxCost && spot.cost_per_hour > preferences.maxCost) {
                score -= 50; // Hard penalty
                reasons.push("Exceeds max cost");
            }

            // Availability Bonus
            if (spot.availability_score > 0.8) {
                score += 10;
                reasons.push("High availability");
            } else if (spot.availability_score < 0.2) {
                score -= 20;
                reasons.push("Likely full");
            }

            return {
                ...spot,
                score: Math.round(score),
                travelTimeMinutes: Math.round(travelMinutes),
                reasons: reasons.slice(0, 3) // Top 3 reasons
            };
        }));

        // Sort by Score Descending
        rankedSpots.sort((a, b) => b.score - a.score);

        return NextResponse.json(rankedSpots);

    } catch (error: any) {
        console.error("Recommendation error:", error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
