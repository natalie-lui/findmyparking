const API_KEY = process.env.OPENWEATHER_API_KEY;
const BASE_URL = 'https://api.openweathermap.org/data/2.5/weather';

export interface WeatherData {
    condition: string; // 'Rain', 'Clear', 'Clouds', etc.
    description: string;
    temp: number; // Celsius
    isRaining: boolean;
}

export async function getWeather(lat: number, lon: number): Promise<WeatherData | null> {
    if (!API_KEY) {
        console.warn("OPENWEATHER_API_KEY is not set. Returning mock weather data.");
        // Mock data for development/demo if key is missing
        return {
            condition: 'Clear',
            description: 'clear sky',
            temp: 22,
            isRaining: false
        };
    }

    try {
        const response = await fetch(`${BASE_URL}?lat=${lat}&lon=${lon}&units=metric&appid=${API_KEY}`);
        if (!response.ok) {
            throw new Error(`Weather API error: ${response.statusText}`);
        }
        const data = await response.json();

        const condition = data.weather[0]?.main || 'Clear';

        return {
            condition,
            description: data.weather[0]?.description || '',
            temp: data.main.temp,
            isRaining: condition === 'Rain' || condition === 'Drizzle' || condition === 'Thunderstorm'
        };

    } catch (error) {
        console.error("Failed to fetch weather:", error);
        return null;
    }
}
