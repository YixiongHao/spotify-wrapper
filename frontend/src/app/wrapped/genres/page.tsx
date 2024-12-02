'use client';
import React, { useEffect, useState } from 'react';
import { useRouter } from "next/navigation";
import Image from "next/image";

export default function Genres() {
    const [genres, setGenres] = useState<string[]>([]);
    const [desc, setDesc] = useState<string>("");
    const [id, setId] = useState<string | null>(null);
    const [isDuo, setIsDuo] = useState<boolean | null>(null);
    const [timeRange, setTimeRange] = useState<number>(2);
    // Add state for window dimensions
    const [dimensions, setDimensions] = useState({ width: 300, height: 300 }); // Default values

    const router = useRouter();

    // Combine localStorage access into one useEffect
    useEffect(() => {
        const storedId = localStorage.getItem("id");
        const duo = localStorage.getItem("isDuo");
        const storedTimeRange = localStorage.getItem("timeRange");

        if (storedId) setId(storedId);
        if (duo) setIsDuo(duo === 'true');
        if (storedTimeRange) setTimeRange(parseInt(storedTimeRange, 10));

        // Set window dimensions
        setDimensions({
            width: window.screen.width/3,
            height: window.screen.height/3
        });
    }, []);

    useEffect(() => {
        const handleClick = () => {
            router.push('/wrapped/tracks/');
        };
        document.addEventListener('click', handleClick);
        return () => document.removeEventListener('click', handleClick);
    }, [router]);

    useEffect(() => {
        if (id && isDuo !== null) {
            fetchFavoriteGenres(id).catch(console.error);
        }
    }, [id, isDuo]);

    async function fetchFavoriteGenres(id: string): Promise<void> {
        try {
            const duo = localStorage.getItem("isDuo") == '1' ? 'true' : 'false';
            const response = await fetch(`http://localhost:8000/spotify_data/displaygenres?id=${id}&isDuo=${duo}`, {
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
            setGenres(data.genres || []);
            setDesc(data.desc || "");
        } catch (error) {
            console.error("Error fetching SpotifyUser data:", error);
        }
    }

    return (
        <div className={"flex flex-col justify-center items-center space-y-2 mt-10"}>
            <p>top genres: {genres}</p>
            <Image
                src="/images/dumpster.png"
                alt={"A dumpster with garbage bags around it"}
                width={dimensions.width}
                height={dimensions.height}
                className={""}
            />
            <p className={"w-3/4"}>{desc}</p>
        </div>
    );
}