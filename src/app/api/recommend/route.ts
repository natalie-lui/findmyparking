import { createClient } from '@supabase/supabase-js';
import { NextRequest, NextResponse } from 'next/server';
import { getWeather } from '@/lib/weather';
import { getTravelTime } from '@/lib/traffic';


const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export async function POST(req: NextRequest) {
    try {
        const body = await req.json();
        const { lat, lng, preferences } = body;


        if (!lat || !lng) {
            return NextResponse.json({ error: "Location (lat, lng) is required" }, { status: 400 });
        }


        const weather = await getWeather(lat, lng);
        const isRaining = weather?.isRaining || false;
        const isHot = (weather?.temp || 0) > 30;



        let spots: any[] = [];

        const { data: rpcData, error: rpcError } = await supabase
            .rpc('nearby_spots', { lat, long: lng, radius_meters: preferences?.maxDistance || 2000 });

        if (!rpcError && rpcData) {
            spots = rpcData;
        } else {
        }


        const rankedSpots = await Promise.all(spots.map(async (spot) => {
            let score = 0;
            let reasons: string[] = [];



            let spotLat = lat;
            let spotLng = lng;
            // Primitive parsing for demo resilience
            if (typeof spot.location === 'string' && spot.location.startsWith('POINT')) {
                const parts = spot.location.replace('POINT(', '').replace(')', '').split(' ');
                spotLng = parseFloat(parts[0]);
                spotLat = parseFloat(parts[1]);
            }

            const traffic = await getTravelTime(lat, lng, spotLat, spotLng);
            const travelTime = traffic?.duration || 0;
            const isTrafficHeavy = traffic?.trafficCongestion === 'heavy' || traffic?.trafficCongestion === 'severe';

            score = 70;

            const travelMinutes = travelTime / 60;
            score -= travelMinutes * 2;
            if (travelMinutes < 5) score += 10;

            if (isTrafficHeavy) {
                score -= 15;
                reasons.push("Heavy traffic on route");
            }

            score -= spot.cost_per_hour * 2;
            if (spot.cost_per_hour < 3) {
                score += 5;
                reasons.push("Low cost");
            }

            const features = spot.features || [];
            const isCovered = features.includes("Covered");
            const isUncovered = features.includes("Uncovered");

            if (isRaining) {
                if (isCovered) {
                    score += 30; // HUGE bonus
                    reasons.push("Covered parking (Good for Rain)");
                } else {
                    score -= 20; // Penalty
                    reasons.push("Uncovered during rain");
                }
            }

            if (preferences?.maxCost && spot.cost_per_hour > preferences.maxCost) {
                score -= 50;
                reasons.push("Exceeds max cost");
            }


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
                reasons: reasons.slice(0, 3)
            };
        }));


        rankedSpots.sort((a, b) => b.score - a.score);

        return NextResponse.json(rankedSpots);

    } catch (error: any) {
        console.error("Recommendation error:", error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
