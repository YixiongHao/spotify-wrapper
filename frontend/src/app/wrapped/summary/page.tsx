'use client';
import React, { useEffect, useState } from 'react';
import { useRouter } from "next/navigation";
import SummaryComponent from "@/app/Components/Summary";

// Define the type for the summary data
type SummaryData = {
    artists: string[];
    tracks: string[];
    quirky: string;
    genres: string[];
};

export default function Summary() {
    const router = useRouter();
    const [desc, setDesc] = useState<SummaryData | null>(null);
    const [id, setId] = useState<string | null>(null); // State to store `id`
    const [isDuo, setIsDuo] = useState<boolean | null>(null);


    // Handle click to navigate to the dashboard
    useEffect(() => {
        const handleClick = () => {
            router.push('/dashboard/');
        };
        document.addEventListener('click', handleClick);

        return () => {
            document.removeEventListener('click', handleClick);
        };
    }, [router]);

    // Retrieve `id` from localStorage
    useEffect(() => {
        const storedId = localStorage.getItem("id");
        if (storedId) {
            setId(storedId);
        }
    }, []);

    // Fetch the summary data once `id` is available
    useEffect(() => {
        const duo = localStorage.getItem("isDuo") == '1' ? 'true' : 'false';
        if (duo) {
            setIsDuo(duo === 'true');
        }
    }, []);

    useEffect(() => {
        if (id && isDuo !== null) {
            fetchSummary(id).catch(console.error);
        }
    }, [id]);

    async function fetchSummary(id: string): Promise<void> {
        const duo = localStorage.getItem("isDuo") == '1' ? 'true' : 'false';
        try {
            const response = await fetch(`http://localhost:8000/spotify_data/displaysummary?id=${id}&isDuo=${duo}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
            });

            if (!response.ok) {
                console.error("Failed to fetch SpotifyUser data");
                return;
            }
            const data = await response.json();
            console.log('Data fetched successfully:', data);
            setDesc(data);
        } catch (error) {
            console.error("Error fetching SpotifyUser data:", error);
        }
    }

    return (
        <div className="flex flex-row justify-center">
            {desc ? (
                <SummaryComponent
                    artists={desc.artists}
                    tracks={desc.tracks}
                    quirky={desc.quirky}
                    genres={desc.genres}
                />
            ) : (
                <p>Loading summary...</p>
            )}
        </div>
    );
}
