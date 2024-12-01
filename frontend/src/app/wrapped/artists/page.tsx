'use client';
import React, { useEffect, useState } from 'react';
import { useRouter } from "next/navigation";
import Artist from "@/app/Components/Artist";

export default function Artists() {
    const router = useRouter();
    const [artists, setArtists] = useState<any[]>([]);
    const [id, setId] = useState<string | null>(null);
    const [isDuo, setIsDuo] = useState<boolean | null>(null);

    useEffect(() => {
        const handleClick = () => {
            router.push('/wrapped/artists2/');
        };
        document.addEventListener('click', handleClick);

        return () => {
            document.removeEventListener('click', handleClick);
        };
    }, [router]);

    // Load `id` from localStorage and fetch artists when it's ready
    useEffect(() => {
        const storedId = localStorage.getItem("id");
        if (storedId) {
            setId(storedId);
        }
    }, []);

    useEffect(() => {
        const duo = localStorage.getItem("isDuo");
        if (duo) {
            setIsDuo(duo === 'true');
        }
    }, []);

    useEffect(() => {
        if (id && isDuo !== null) {
            fetchFavoriteArtists(id).catch(console.error);
        }
    }, [id]);

    async function fetchFavoriteArtists(id: string): Promise<void> {
        try {
            const response = await fetch(`https://spotify-wrapped-backend.vercel.app/spotify_data/displayartists?id=${id}&isDuo=${isDuo}`, {
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
            setArtists(data.slice(0, 2));
            localStorage.setItem("artistsList", JSON.stringify(data.slice(2,4)));
        } catch (error) {
            console.error("Error fetching SpotifyUser data:", error);
        }
    }
    return (
        <div className={"flex flex-row justify-center"}>
            {artists.length > 0 ? (
                artists.map((artist: { name: string; image: string; desc: string; }, index: number) => (
                    <Artist
                        key={index}
                        name={artist.name}
                        img={artist.image} // Ensure `image` matches your API response
                        desc={artist.desc}
                        rank={index + 1}
                    />
                ))
            ) : (
                <p>Loading artists...</p>
            )}
        </div>
    );
}
