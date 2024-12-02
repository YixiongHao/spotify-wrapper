import React from "react";
import Image from "next/image";

type ComparisonProps = {
    name1: string;
    name2: string;
    img1: string;
    img2: string;
    sub1?: string;
    sub2?: string;
    desc: string;
}

/**
 * Returns a React element containing a div which contains
 */
function Comparison(props: ComparisonProps) {
    return (
        <div className={"flex flex-col items-center justify-items mt-10 space-y-6"}>
            <div className={"flex flex-row mb-5 space-x-5 items-center justify-center"}>
                <Image
                    src={props.img1}
                    alt={"A picture of " + props.name1}
                    width={120}
                    height={120}
                    className={"border-4 border-black object-contain"}
                />
                <div className={"mt-auto mb-auto w-fit"}>
                    <p className={"text-5xl normal-case mt-auto mb-auto"}>{props.name1}</p>
                    <p className={"text-2xl normal-case"}>{props.sub1 ? props.sub1 : ""}</p>
                </div>
                <p className={"text-5xl normal-case mt-auto mb-auto"}>vs</p>
                <Image
                    src={props.img2}
                    alt={"A picture of " + props.name2}
                    width={120}
                    height={120}
                    className={"border-4 border-black object-contain"}
                />
                <div className={"mt-auto mb-auto w-fit"}>
                    <p className={"text-5xl normal-case mt-auto mb-auto"}>{props.name2}</p>
                    <p className={"text-2xl normal-case"}>{props.sub2 ? props.sub2 : ""}</p>
                </div>
            </div>
                <p className={"items-start w-3/4"}>{props.desc}</p>
        </div>
    );
}

export default Comparison;