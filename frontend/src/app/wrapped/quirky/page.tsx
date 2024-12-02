'use client';
import React, { useEffect, useState } from 'react';
import { useRouter } from "next/navigation";

export default function Quirky() {
    const [desc, setDesc] = useState<string>(""); // Assuming desc is a string
    const [id, setId] = useState<string | null>(null); // State to store `id`
    const [isDuo, setIsDuo] = useState<boolean | null>(null);

    const router = useRouter();

    // Handle click event to navigate to the next page
    useEffect(() => {
        const handleClick = () => {
            router.push('/wrapped/summary/');
        };
        document.addEventListener('click', handleClick);

        return () => {
            document.removeEventListener('click', handleClick);
        };
    }, [router]);

    // Load `id` from localStorage
    useEffect(() => {
        const storedId = localStorage.getItem("id");
        if (storedId) {
            setId(storedId);
        }
    }, []);

    useEffect(() => {
        const duo = localStorage.getItem("isDuo") == '1' ? 'true' : 'false';
        if (duo) {
            setIsDuo(duo === 'true');
        }
    }, []);

    useEffect(() => {
        if (id && isDuo !== null) {
            fetchQuirkyDescription(id).catch(console.error);
        }
    }, [id]);

    const [timeRange, setTimeRange] = useState<number>(2);

    // Load `timeRange` from localStorage
    useEffect(() => {
        const storedTimeRange = localStorage.getItem("timeRange");
        if (storedTimeRange) {
            setTimeRange(parseInt(storedTimeRange, 10));
        }
    }, []);

    async function fetchQuirkyDescription(id: string): Promise<void> {
        const duo = localStorage.getItem("isDuo") == '1' ? 'true' : 'false';
        try {
            const response = await fetch(`http://localhost:8000/spotify_data/displayquirky?id=${id}&isDuo=${duo}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include'
            });

            if (!response.ok) {
                console.error("Failed to fetch SpotifyUser data");
                return;
            }
            const data = await response.json();
            console.log('everything went alright');
            console.log(data);

            setDesc(data || "No description available");
        } catch (error) {
            console.error("Error fetching SpotifyUser data:", error);
        }
    }

    return (
        <div className="flex flex-col items-center">
            <h1 className="text-2xl font-bold mb-4">Your Quirky Feature</h1>
            <p className="text-lg italic mb-4">{desc}</p>
            <img
                src="../../images/trashcan.png"
                alt="trash graphic"
                style={{ maxWidth: "20%", height: "auto", marginTop: "20px" }}
            />
        </div>
    );
}
