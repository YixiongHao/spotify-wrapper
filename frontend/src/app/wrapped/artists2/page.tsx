'use client';
import React, { useEffect, useState } from 'react';
import { useRouter } from "next/navigation";
import Artist from "@/app/Components/Artist";
import Comparison from "@/app/Components/Comparison";
import Loading from "@/app/Components/Loading";

export default function Artists2() {
    const router = useRouter();
    const [artists, setArtists] = useState<any[]>([]);
    const [isDuo, setIsDuo] = useState<boolean | null>(null);

    useEffect(() => {
        const duo = localStorage.getItem("isDuo") == '1' ? 'true' : 'false';
        if (duo) {
            setIsDuo(duo === 'true');
        }
    }, []);

    useEffect(() => {
        const handleClick = () => {
            router.push('/wrapped/genres/');
        };
        document.addEventListener('click', handleClick);

        return () => {
            document.removeEventListener('click', handleClick);
        };
    }, [router]);

    // Load remaining artists from localStorage
    useEffect(() => {
        const artistsList = localStorage.getItem("artistsList");
        if (artistsList) {
            setArtists(JSON.parse(artistsList));
        }
    }, []);

    if (isDuo) {
        return(<>
            {artists.length > 0 ? (
                <Comparison name1={artists[0].name} name2={artists[1].name} img1={artists[0].image} img2={artists[1].image} desc={artists[0].desc}/>
                ) : (
                    <Loading text={"artist comparisons"}/>
                )}
        </>);
    } else {
        return (
            <div className={"flex flex-row justify-center"}>
                {artists.length > 0 ? (
                    artists.map((artist: { name: string; image: string; desc: string; }, index: number) => (
                        <Artist
                            key={index}
                            name={artist.name}
                            img={artist.image} // Ensure `image` matches your API response
                            desc={artist.desc}
                            rank={index + 3}
                        />
                    ))
                ) : (
                    <Loading text={"artists"}/>
                )}
            </div>
        );
    }
}
