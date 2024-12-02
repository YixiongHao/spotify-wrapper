'use client';
import React, { useEffect, useState } from 'react';
import Track from "@/app/Components/Track";
import { useRouter } from "next/navigation";
import Comparison from "@/app/Components/Comparison";
import Loading from "@/app/Components/Loading";

export default function Tracks2() {
    const [tracks, setTracks] = useState<any[]>([]);
    const router = useRouter();
    const [isDuo, setIsDuo] = useState<boolean | null>(null);

    useEffect(() => {
        const duo = localStorage.getItem("isDuo") == '1' ? 'true' : 'false';
        if (duo) {
            setIsDuo(duo === 'true');
        }
    }, []);

    // Handle click to navigate to the next page
    useEffect(() => {
        const handleClick = () => {
            router.push('/wrapped/quirky/');
        };
        document.addEventListener('click', handleClick);

        return () => {
            document.removeEventListener('click', handleClick);
        };
    }, [router]);

    // Retrieve remaining tracks from localStorage
    useEffect(() => {
        const tracksList = localStorage.getItem("tracksList");
        if (tracksList) {
            setTracks(JSON.parse(tracksList));
        }
    }, []);

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
                            rank={index + 3}
                        />
                    ))
                ) : (
                    <p>Loading tracks...</p>
                )}
            </div>
        );
    }
}
