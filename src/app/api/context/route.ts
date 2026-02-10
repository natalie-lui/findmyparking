import { NextRequest, NextResponse } from 'next/server';
import { getWeather } from '@/lib/weather';
// import { getTraffic } from '@/lib/traffic'; // Traffic usually requires start/end, so maybe just general congestion or skip for general context

export async function GET(req: NextRequest) {
    const { searchParams } = new URL(req.url);
    const lat = parseFloat(searchParams.get('lat') || '0');
    const lng = parseFloat(searchParams.get('lng') || '0');

    if (!lat || !lng) {
        return NextResponse.json({ error: "Lat/Lng required" }, { status: 400 });
    }

    // Fetch weather only for context widget
    const weather = await getWeather(lat, lng);

    // Traffic could be fetched if we had a specific "commute" route, but for general context, maybe just skip or use a fixed point?
    // Let's just return weather for the "Live Context" widget for now.

    return NextResponse.json({
        weather,
        timestamp: new Date().toISOString()
    });
}
