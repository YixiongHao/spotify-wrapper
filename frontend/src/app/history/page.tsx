'use client';
import React, { useEffect, useState } from 'react';
import { useRouter } from "next/navigation";
import Heading1 from '../Components/Heading1';

export default function History() {
    const [history, setHistory] = useState<{ id: number, isDuo: boolean }[]>([]);
    const [popupMessage, setPopupMessage] = useState<string | null>(null);
    const router = useRouter();

    async function fetchSummary(): Promise<void> {
        try {
            const response = await fetch(`https://spotify-wrapped-backend.vercel.app/spotify_data/displayhistory`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
            });

            if (!response.ok) {
                if (response.status === 500) {
                    setPopupMessage("No history for this account. Go create a roast!");
                } else {
                    console.error("Failed to fetch SpotifyUser data");
                }        
                return;
            }
            const data = await response.json();
            console.log('Data fetched successfully:', data);
            setHistory(data); // Update state with the fetched data
        } catch (error) {
            console.error("Error fetching SpotifyUser data:", error);
        }
    }

    useEffect(() => {
        fetchSummary().catch(console.error);
    }, []);

    const handleButtonClick = (value: number) => {
        // Store the clicked value in localStorage
        localStorage.setItem('id', value.toString());
        localStorage.setItem('isDuo', 'true');

        // Redirect to another page
        router.push('/wrapped/title');
    };

    return (
        <>
            <Heading1 text="Past Roasts" />
            <p>Roast history information</p>
            <div className="flex flex-wrap gap-2 mt-4">
                {history.map((item, index) => (
                    <button
                        key={index}
                        onClick={() => handleButtonClick(item.id)}
                        className={`px-4 py-2 rounded text-white hover:opacity-90 ${
                            item.isDuo ? 'bg-green-500' : 'bg-blue-500'
                        }`}
                    >
                        {item.id}
                    </button>
                ))}
            </div>
            {popupMessage && (
                <div className="mt-4 p-4 bg-red-500 text-white rounded">
                    {popupMessage}
                </div>
            )}
        </>
    );
}
