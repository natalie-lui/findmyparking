const MAPBOX_TOKEN = process.env.MAPBOX_ACCESS_TOKEN;
const BASE_URL = 'https://api.mapbox.com/directions/v5/mapbox/driving-traffic';

export interface TrafficData {
    duration: number; // seconds, including traffic
    distance: number; // meters
    trafficCongestion: 'low' | 'moderate' | 'heavy' | 'severe';
}

export async function getTravelTime(startLat: number, startLng: number, endLat: number, endLng: number): Promise<TrafficData | null> {
    if (!MAPBOX_TOKEN) {
        console.warn("MAPBOX_ACCESS_TOKEN is not set. Returning mock traffic data.");
        // Mock linear distance-based time
        const dist = Math.sqrt(Math.pow(endLat - startLat, 2) + Math.pow(endLng - startLng, 2)) * 111000; // rough meters
        const speed = 10; // m/s (~36km/h)
        return {
            duration: dist / speed,
            distance: dist,
            trafficCongestion: 'moderate'
        };
    }

    try {
        const start = `${startLng},${startLat}`;
        const end = `${endLng},${endLat}`;
        const url = `${BASE_URL}/${start};${end}?access_token=${MAPBOX_TOKEN}&geometries=geojson&overview=full`;

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Traffic API error: ${response.statusText}`);
        }
        const data = await response.json();

        if (!data.routes || data.routes.length === 0) return null;

        const route = data.routes[0];
        const duration = route.duration; // seconds
        const distance = route.distance; // meters

        // Naive congestion estimation: compare duration vs typical duration (if available) or just speed
        // Mapbox provides `duration_typical` if requested, but let's just use duration for now.
        // If standard speed is ~15m/s (54km/h) context, check actual speed.
        const speed = distance / duration;
        let congestion: TrafficData['trafficCongestion'] = 'low';

        if (speed < 5) congestion = 'severe'; // < 18km/h
        else if (speed < 10) congestion = 'heavy'; // < 36km/h
        else if (speed < 15) congestion = 'moderate';

        return {
            duration,
            distance,
            trafficCongestion: congestion
        };

    } catch (error) {
        console.error("Failed to fetch traffic:", error);
        return null;
    }
}
