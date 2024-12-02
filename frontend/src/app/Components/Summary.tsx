// Summary.tsx
import React from "react";
import Heading2 from "@/app/Components/Heading2";

type SummaryComponentProps = {
    artists: string[];
    tracks: string[];
    quirky: string;
    genres: string[];
};

const SummaryComponent: React.FC<SummaryComponentProps> = ({ artists, tracks, quirky, genres }) => {
    return (
        <div className={"flex flex-col min-h-screen items-center justify-center"}>
        <div className={"flex flex-row items-center justify-center space-x-10 text-center"}>
            <div>
            <Heading2 text = {"Top Artists"}/>
            <ul>
                {artists.map((artist, index) => (
                    <li key={index}>{artist}</li>
                ))}
            </ul>
                </div>
            <div>
            <Heading2 text = {"Top Tracks"}/>
            <ul>
                {tracks.map((track, index) => (
                    <li key={index}>{track}</li>
                ))}
            </ul>
                </div>
            <div>
            <Heading2 text = {"Quirky Favorite"}/>
            <p>{quirky}</p>
                </div>
            <div>
            <Heading2 text = {"Top Genres"}/>
            <ul>
                {genres.map((genre, index) => (
                    <li key={index}>{genre}</li>
                ))}
            </ul>
                </div>
        </div>
        </div>
    );
};

export default SummaryComponent;
