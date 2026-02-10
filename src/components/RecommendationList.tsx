import { LucideIcon, MapPin, DollarSign, CloudRain, Clock } from 'lucide-react';

interface ReasonProps {
    text: string;
}

const ReasonBadge = ({ text }: ReasonProps) => {
    let color = "bg-gray-100 text-gray-800";
    if (text.includes("Rain")) color = "bg-blue-100 text-blue-800";
    if (text.includes("Cost")) color = "bg-green-100 text-green-800";
    if (text.includes("Heavy")) color = "bg-red-100 text-red-800";

    return (
        <span className={`text-xs px-2 py-1 rounded-full ${color} mr-1 mb-1 inline-block`}>
            {text}
        </span>
    );
};

interface RecommendationListProps {
    spots: any[];
    isLoading: boolean;
    onSelect: (spot: any) => void;
}

export default function RecommendationList({ spots, isLoading, onSelect }: RecommendationListProps) {
    if (isLoading) {
        return <div className="p-4 text-center">Finding best spots based on real-time context...</div>;
    }

    if (spots.length === 0) {
        return <div className="p-4 text-center text-gray-500">No parking spots found nearby.</div>;
    }

    return (
        <div className="space-y-4 p-4 overflow-y-auto h-full pb-20">
            {spots.map((spot, index) => (
                <div
                    key={spot.id}
                    className={`border rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer bg-white ${index === 0 ? 'border-primary ring-2 ring-primary/20' : ''}`}
                    onClick={() => onSelect(spot)}
                >
                    <div className="flex justify-between items-start">
                        <div>
                            <h3 className="font-bold text-lg flex items-center">
                                {index + 1}. {spot.name}
                            </h3>
                            <p className="text-sm text-gray-500 flex items-center mt-1">
                                <MapPin size={14} className="mr-1" /> {spot.travelTimeMinutes} mins away
                            </p>
                        </div>
                        <div className="text-right">
                            <div className="font-bold text-lg flex items-center justify-end text-green-600">
                                <DollarSign size={16} />{spot.cost_per_hour}
                                <span className="text-xs text-gray-400 font-normal ml-1">/hr</span>
                            </div>
                            <div className="text-xs font-bold bg-gray-100 rounded px-1 mt-1 text-center">Score: {spot.score}</div>
                        </div>
                    </div>

                    {spot.image_url && (
                        <div className="mt-2 h-32 w-full rounded-md overflow-hidden relative">
                            <img src={spot.image_url} alt={spot.name} className="object-cover w-full h-full" />
                        </div>
                    )}

                    <div className="mt-3">
                        <div className="flex flex-wrap">
                            {spot.reasons && spot.reasons.map((r: string, i: number) => (
                                <ReasonBadge key={i} text={r} />
                            ))}
                        </div>
                    </div>

                    <div className="mt-2 text-xs text-gray-400">
                        Capacity: {spot.capacity} | {spot.features.join(", ")}
                    </div>
                </div>
            ))}
        </div>
    );
}
