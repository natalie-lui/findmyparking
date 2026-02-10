"use client";

import { useEffect, useState } from 'react';
import { Cloud, Sun, CloudRain, Wind, Thermometer } from 'lucide-react';

interface ContextData {
    weather: {
        condition: string;
        temp: number;
        description: string;
    };
    timestamp: string;
}

export default function ContextWidget({ lat, lng }: { lat: number; lng: number }) {
    const [data, setData] = useState<ContextData | null>(null);

    useEffect(() => {
        if (!lat || !lng) return;

        fetch(`/api/context?lat=${lat}&lng=${lng}`)
            .then(res => res.json())
            .then(setData)
            .catch(console.error);
    }, [lat, lng]);

    if (!data) return null;

    const { weather } = data;

    let Icon = Sun;
    if (weather.condition === 'Rain') Icon = CloudRain;
    if (weather.condition === 'Clouds') Icon = Cloud;

    return (
        <div className="absolute top-4 right-4 z-[1000] bg-white/90 backdrop-blur-md p-3 rounded-xl shadow-lg border border-gray-200 flex items-center gap-3">
            <div className="bg-blue-100 p-2 rounded-full text-blue-600">
                <Icon size={24} />
            </div>
            <div>
                <div className="font-bold text-sm">{weather.temp.toFixed(1)}°C</div>
                <div className="text-xs text-gray-500 capitalize">{weather.description}</div>
            </div>

            {/* Mock Traffic Indicator since we don't have a specific route yet */}
            <div className="h-8 w-[1px] bg-gray-200 mx-1"></div>
            <div className="flex flex-col items-center">
                <div className="text-xs font-bold text-gray-600">Traffic</div>
                <div className="flex gap-1 mt-1">
                    <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                    <span className="text-[10px] text-green-600">Normal</span>
                </div>
            </div>
        </div>
    );
}
