import React from "react";

type LoadingProps = {
    text?: string;
}

/**
 * Returns a React element containing a styled h1 tag with the given text
 */
function Loading(props : LoadingProps) {

    return (
        <div className={"flex flex-col min-h-screen items-center justify-center lowercase"}>
            Loading{props.text ? " " + props.text : ""}...
        </div>
    );
}

export default Loading;