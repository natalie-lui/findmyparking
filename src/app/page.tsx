"use client";

import { AppProvider, useApp } from '@/context/AppContext';
import dynamic from 'next/dynamic';
import { useEffect, useState } from 'react';
import RecommendationList from '@/components/RecommendationList';
import ContextWidget from '@/components/ContextWidget';
import { Settings, Filter } from 'lucide-react';

// Dynamic import for Map to avoid SSR issues with Leaflet
const Map = dynamic(() => import('@/components/Map'), { ssr: false });

function HomeContent() {
  const { location, preferences, updatePreferences, isLoadingLocation, error } = useApp();
  const [spots, setSpots] = useState([]);
  const [loadingSpots, setLoadingSpots] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    if (location) {
      setLoadingSpots(true);
      fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lat: location.lat,
          lng: location.lng,
          preferences
        })
      })
        .then(res => res.json())
        .then(data => {
          setSpots(data);
          setLoadingSpots(false);
        })
        .catch(err => {
          console.error(err);
          setLoadingSpots(false);
        });
    }
  }, [location, preferences]);

  if (isLoadingLocation) {
    return <div className="flex items-center justify-center h-screen">Locating you...</div>;
  }

  if (error) {
    return <div className="flex items-center justify-center h-screen text-red-500">{error}</div>;
  }

  return (
    <div className="flex h-screen flex-col md:flex-row">
      {/* Sidebar / List */}
      <div className="w-full md:w-1/3 lg:w-1/4 h-1/2 md:h-full bg-white border-r flex flex-col relative z-20 shadow-xl">
        <div className="p-4 border-b bg-gray-50 flex justify-between items-center">
          <h1 className="font-bold text-xl bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
            FindMyParking
          </h1>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 hover:bg-gray-200 rounded-full transition-colors"
            title="Preferences"
          >
            <Settings size={20} className="text-gray-600" />
          </button>
        </div>

        {/* Preferences Panel (Collapsible) */}
        {showSettings && (
          <div className="p-4 bg-gray-100 border-b space-y-3 animate-in slide-in-from-top duration-300">
            <h3 className="font-semibold text-sm text-gray-700 flex items-center gap-2">
              <Filter size={14} /> Ranking Priorities
            </h3>

            <div className="flex flex-col gap-2">
              <label className="flex items-center justify-between text-sm">
                Max Cost ($/hr)
                <input
                  type="number"
                  className="w-16 p-1 border rounded text-right"
                  value={preferences.maxCost || ''}
                  onChange={(e) => updatePreferences({ maxCost: parseFloat(e.target.value) })}
                />
              </label>
              <label className="flex items-center gap-2 text-sm cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.covered || false}
                  onChange={(e) => updatePreferences({ covered: e.target.checked })}
                />
                Prefer Covered (Garages)
              </label>
            </div>
          </div>
        )}

        <div className="flex-1 overflow-hidden">
          <RecommendationList
            spots={spots}
            isLoading={loadingSpots}
            onSelect={(spot) => {
              // Logic to fly to spot handled via state passing or event bus, 
              // for simplicity we just log or highlight in future.
              // Ideally pass simple state up.
              console.log("Selected", spot);
            }}
          />
        </div>
      </div>

      {/* Map View */}
      <div className="flex-1 h-1/2 md:h-full relative z-10">
        {location && (
          <>
            <Map
              center={location}
              spots={spots}
              onSpotSelect={(spot) => console.log("Map Select", spot)}
            />
            <ContextWidget lat={location.lat} lng={location.lng} />
          </>
        )}
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <AppProvider>
      <HomeContent />
    </AppProvider>
  );
}
