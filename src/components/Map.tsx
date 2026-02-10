"use client";

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for Leaflet icon not found in Next.js
const icon = L.icon({
    iconUrl: '/images/marker-icon.png',
    shadowUrl: '/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

// Component to update map view when location changes
function MapController({ center }: { center: { lat: number, lng: number } }) {
    const map = useMap();
    useEffect(() => {
        map.flyTo(center, 15);
    }, [center, map]);
    return null;
}

interface MapProps {
    center: { lat: number; lng: number };
    spots: any[];
    onSpotSelect: (spot: any) => void;
}

const Map = ({ center, spots, onSpotSelect }: MapProps) => {
    // Leaflet requires window, so this component must be dynamically imported with ssr: false
    // But inside this file we can assume client-side execution if loaded correctly.

    // Custom Icon for parking spots
    const parkingIcon = new L.Icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    const userIcon = new L.Icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    return (
        <MapContainer center={center} zoom={15} style={{ height: '100%', width: '100%' }}>
            <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />

            <MapController center={center} />

            {/* User Location */}
            <Marker position={center} icon={userIcon}>
                <Popup>You are here</Popup>
            </Marker>

            {/* Parking Spots */}
            {spots.map((spot) => {
                // Parse location if it's WKT string or object
                let pos: [number, number] = [center.lat, center.lng];
                if (typeof spot.location === 'string' && spot.location.startsWith('POINT')) {
                    const parts = spot.location.replace('POINT(', '').replace(')', '').split(' ');
                    pos = [parseFloat(parts[1]), parseFloat(parts[0])]; // Lat, Lng
                }

                return (
                    <Marker
                        key={spot.id}
                        position={pos}
                        icon={parkingIcon}
                        eventHandlers={{
                            click: () => onSpotSelect(spot),
                        }}
                    >
                        <Popup>
                            <strong>{spot.name}</strong><br />
                            ${spot.cost_per_hour}/hr<br />
                            Score: {spot.score}
                        </Popup>
                    </Marker>
                );
            })}
        </MapContainer>
    );
};

export default Map;
