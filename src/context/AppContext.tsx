"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface UserPreferences {
    maxCost?: number;
    maxDistance?: number;
    covered?: boolean;
    accessible?: boolean;
    ev?: boolean;
}

interface AppContextType {
    location: { lat: number; lng: number } | null;
    setLocation: (loc: { lat: number; lng: number } | null) => void;
    preferences: UserPreferences;
    updatePreferences: (prefs: Partial<UserPreferences>) => void;
    isLoadingLocation: boolean;
    error: string | null;
}

const defaultPreferences: UserPreferences = {
    maxCost: 20,
    maxDistance: 1000,
    covered: false,
    accessible: false,
    ev: false,
};

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
    const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null);
    const [preferences, setPreferences] = useState<UserPreferences>(defaultPreferences);
    const [isLoadingLocation, setIsLoadingLocation] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!navigator.geolocation) {
            setError("Geolocation is not supported by your browser");
            setIsLoadingLocation(false);
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                setLocation({
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                });
                setIsLoadingLocation(false);
            },
            (err) => {
                setError("Unable to retrieve your location");
                setIsLoadingLocation(false);
                // Default to UCI if location fails for demo
                setLocation({ lat: 33.6405, lng: -117.8443 });
            }
        );
    }, []);

    const updatePreferences = (newPrefs: Partial<UserPreferences>) => {
        setPreferences((prev) => ({ ...prev, ...newPrefs }));
    };

    return (
        <AppContext.Provider value={{ location, setLocation, preferences, updatePreferences, isLoadingLocation, error }}>
            {children}
        </AppContext.Provider>
    );
}

export function useApp() {
    const context = useContext(AppContext);
    if (context === undefined) {
        throw new Error('useApp must be used within an AppProvider');
    }
    return context;
}
