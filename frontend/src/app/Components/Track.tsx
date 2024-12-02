import React from "react";
import Image from "next/image";

type TrackProps = {
    name: string;
    artist: string;
    img: string;
    desc: string;
    rank: number;
}

/**
 * Returns a React element containing a div which contains an artist's name, rank, image, and LLM roast
 *
 * @param props.name the track's name
 * @param props.artist artist name
 * @param props.img the url to the track image
 * @param props.desc the LLM-generated roast of the track
 * @param props.rank the tracks's rank
 */
function Track(props: TrackProps) {
    const altText = "Cover photo for " + props.name;
    return (
        <div className={"flex flex-col m-6 overflow-hidden w-2/5"}>
            <div className={"flex flex-row mb-5 space-x-5"}>
                <p className={"text-7xl text-nowrap mt-auto mb-auto"}>#{props.rank}</p>
                <Image
                    src={props.img}
                    alt={altText}
                    width={120}
                    height={120}
                    className={"border-4 border-black"}
                />
                <div className={"mt-auto mb-auto"}>
                    <p className={"text-5xl normal-case"}>{props.name}</p>
                    <p className={"text-2xl normal-case"}>{props.artist}</p>
                </div>
            </div>
            <p className={"items-start"}>{props.desc}</p>
        </div>
    );
}

export default Track;