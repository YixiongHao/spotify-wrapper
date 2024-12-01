'use client';
import React, { useEffect, useState } from 'react';
import { useRouter } from "next/navigation";

export default function Genres() {
    const [genres, setGenres] = useState<string[]>([]); // Assuming genres is a string array
    const [desc, setDesc] = useState<string>(""); // Description is likely a string
    const [id, setId] = useState<string | null>(null);
    const [isDuo, setIsDuo] = useState<boolean | null>(null);

    const router = useRouter();

    useEffect(() => {
        const storedId = localStorage.getItem("id");
        if (storedId) {
            setId(storedId);
        }
    }, []);

    useEffect(() => {
        const handleClick = () => {
            router.push('/wrapped/tracks/');
        };
        document.addEventListener('click', handleClick);

        return () => {
            document.removeEventListener('click', handleClick);
        };
    }, [router]);

    useEffect(() => {
        const storedTimeRange = localStorage.getItem("timeRange");
        if (storedTimeRange) {
            setTimeRange(parseInt(storedTimeRange, 10));
        }
    }, []);

    const [timeRange, setTimeRange] = useState<number>(2);

    useEffect(() => {
        const duo = localStorage.getItem("isDuo");
        if (duo) {
            setIsDuo(duo === 'true');
        }
    }, []);

    useEffect(() => {
        if (id && isDuo !== null) {
            fetchFavoriteGenres(id).catch(console.error);
        }
    }, [id]);

    async function fetchFavoriteGenres(id: string): Promise<void> {
        try {
            const response = await fetch(`https://spotify-wrapped-backend.vercel.app/spotify_data/displaygenres?id=${id}&isDuo=${isDuo}`, {
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
            console.log('everything went alright');
            console.log(data);

            setGenres(data.genres || []); // Ensure genres is always an array
            setDesc(data.desc || ""); // Default to empty string if no desc
        } catch (error) {
            console.error("Error fetching SpotifyUser data:", error);
        }
    }

    return (
        <div className={"flex flex-row justify-center"}>
            <p>{genres}</p>
            <p>{desc}</p>
            <img 
                src="..\..\images\dumpster.png" 
                alt="dumpster graphic" 
                style={{ maxWidth: "20%", height: "auto", marginTop: "20px" }}
                />
        </div>
    );
}