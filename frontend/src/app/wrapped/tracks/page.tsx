'use client';
import React, { useEffect, useState } from 'react';
import Track from "@/app/Components/Track";
import { useRouter } from "next/navigation";
import Loading from "@/app/Components/Loading";
import Comparison from "@/app/Components/Comparison";

export default function Tracks() {
    const [tracks, setTracks] = useState<any[]>([]);
    const [id, setId] = useState<string | null>(null); // State to store `id`
    const [isDuo, setIsDuo] = useState<boolean | null>(null);

    const router = useRouter();

    // Handle click to navigate to the next page
    useEffect(() => {
        const handleClick = () => {
            router.push('/wrapped/tracks2/');
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

    // Fetch the tracks once `id` is available
    useEffect(() => {
        const duo = localStorage.getItem("isDuo") == '1' ? 'true' : 'false';
        if (duo) {
            setIsDuo(duo === 'true');
        }
    }, []);

    useEffect(() => {
        if (id && isDuo !== null) {
            fetchFavoriteSongs(id).catch(console.error);
        }
    }, [id]);

    const [timeRange, setTimeRange] = useState<number>(2);

    // Retrieve `timeRange` from localStorage
    useEffect(() => {
        const storedTimeRange = localStorage.getItem("timeRange");
        if (storedTimeRange) {
            setTimeRange(parseInt(storedTimeRange, 10));
        }
    }, []);

    async function fetchFavoriteSongs(id: string): Promise<void> {
        const duo = localStorage.getItem("isDuo") == '1' ? 'true' : 'false';
        try {
            const response = await fetch(`http://localhost:8000/spotify_data/displaytracks?id=${id}&isDuo=${duo}`, {
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

            setTracks(data.slice(0, 2));
            localStorage.setItem("tracksList", JSON.stringify(data.slice(2,4)));
        } catch (error) {
            console.error("Error fetching SpotifyUser data:", error);
        }
    }

    if (isDuo) {
        return(<>
            {tracks.length > 0 ? (
                <Comparison name1={tracks[0].name} name2={tracks[1].name} img1={tracks[0].image} img2={tracks[1].image} desc={tracks[0].desc} sub1={tracks[0].artist} sub2={tracks[1].artist}/>
                ) : (
                    <Loading text={"track comparisons"}/>
                )}
        </>);
    } else {
        return (
            <div className={"flex flex-row justify-center"}>
                {tracks.length > 0 ? (
                    tracks.map((track, index) => (
                        <Track
                            key={index}
                            name={track.name}
                            artist={track.artist}
                            img={track.image} // Ensure `image` matches your API response
                            desc={track.desc}
                            rank={index + 1}
                        />
                    ))
                ) : (
                    <Loading text={"tracks"}/>
                )}
            </div>
        );
    }
}
