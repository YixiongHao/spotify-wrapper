import React from "react";
import Image from "next/image";

type ArtistProps = {
    name: string;
    img: string;
    desc: string;
    rank: number;
}

/**
 * Returns a React element containing a div which contains an artist's name, rank, image, and LLM roast
 *
 * @param props.name the artist's name
 * @param props.img the url to the artist image
 * @param props.desc the LLM-generated roast of the artist
 * @param props.rank the artist's rank
 */
function Artist(props: ArtistProps) {
    const altText = props.name + "'s profile picture";
    return (
        <div className={"flex flex-col m-6 overflow-hidden w-2/5"}>
            <div className={"flex flex-row mb-5 space-x-5"}>
                <Image
                    src={props.img}
                    alt={altText}
                    width={120}
                    height={120}
                    className={"border-4 border-black object-contain"}
                />
                <p className={"text-7xl text-nowrap mt-auto mb-auto"}>#{props.rank}</p>
                <p className={"text-5xl normal-case mt-auto mb-auto"}>{props.name}</p>
            </div>
            <p className={"items-start"}>{props.desc}</p>
        </div>
    );
}

export default Artist;