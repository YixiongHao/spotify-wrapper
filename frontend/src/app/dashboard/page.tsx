"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Button from "../Components/Button";
import Heading1 from "../Components/Heading1";
import Radio from "../Components/Radio";
import { getCookie } from "@/utils";
import { logError, logInfo } from "../utils/logger";

export default function Dashboard() {
    const router = useRouter();
    const [isAuthenticated, setIsAuthenticated] = useState(true);
    const [username, setUsername] = useState<string>("Guest");
    const [timeframe, setTimeframe] = useState<number>(2);
    const [otherUser, setOtherUser] = useState("");
    const [popupMessage, setPopupMessage] = useState<string | null>(null);

    useEffect(() => {
        localStorage.setItem("id", "-1");
        localStorage.setItem("isDuo", '0');
    }, []);

    // Fetch username from backend
    useEffect(() => {
        const fetchUsername = async () => {
            try {
                const response = await fetch("http://localhost:8000/spotify/get-username/", {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    credentials: "include",
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                setUsername(data.username);
                localStorage.setItem("user1", data.username);
            } catch (error) {
                console.error("Error fetching username:", error);
            }
        };

        fetchUsername();
    }, []);

    // Load `timeRange` from localStorage
    useEffect(() => {
        const storedTimeframe = localStorage.getItem("timeRange");
        if (storedTimeframe) {
            setTimeframe(parseInt(storedTimeframe, 10));
        }
    }, []);

    // Check authentication
    useEffect(() => {
        fetch("http://localhost:8000/spotify/is-authenticated/", { credentials: "include" })
            .then((response) => response.json())
            .then((data) => {
                if (!data.status) {
                    logInfo("Not authenticated", data);
                    window.location.href = "http://localhost:8000/spotify/get-auth-url/";
                } else {
                    setIsAuthenticated(true);
                }
            })
            .catch((error) => {
                logError("Error:", error);
                router.push("/");
            });
    }, [router]);

    if (!isAuthenticated) {
        return null; // Render a loading spinner or a fallback UI here
    }

    const handleSelection = (value: number) => {
        setTimeframe(value); // Update state
        localStorage.setItem("timeRange", value.toString()); // Save to localStorage
    };

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault(); // Prevent default form submission
        if (otherUser.trim()) {
            console.log(otherUser);
            updateUser();
            const success = await checkUsername(otherUser);
            if (success !== null) {
                localStorage.setItem("isDuo", '1');
                localStorage.setItem("user2", otherUser);
                router.push(`/wrapped/title`); // Navigate to the duo wrapped
            }
        }
    };

    async function checkUsername(username: String) {
        try {
            const response = await fetch(`http://localhost:8000/spotify_data/checkusername?username=${username}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
    
            const data = await response.json();
            if (data.exists) {
                setPopupMessage(null); // Clear popup if username exists
                return 1 // success
            } else {
                setPopupMessage("Username does not exist. Please retype it.");
                return null
            }
        } catch (error) {
            console.error("Error checking username:", error);
        }
    }

    const handleLogoutClick = async () => {
        const csrfToken = getCookie('csrftoken');
    
        try {
          const response = await fetch('http://localhost:8000/spotify/logout/', {
            method: 'GET',
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
              'X-CSRFToken': csrfToken || '',
            },
            credentials: 'include',
          });
    
          if (response.ok) {
            router.push('/');
            const data = await response.json();
            logInfo('Logout Successful:', data);
          } else if (response.status === 400) {
            logInfo('Response:', response);
          } else {
            logInfo('Response:', response);
          }
        } catch (error) {
            logError('Error:', error);
        }
      };
    
      const handleDeleteAccount = async () => {
        try {
            const response = await fetch ('http://localhost:8000/spotify/delete-account/', {
                credentials: 'include'
            });
    
            if (response.ok) {
                router.push('/')
                logInfo('response', response)
            } else {
                logError('Response', response)
            }
        } catch (error) {
            logError('Error', error)
        }
      }

      async function updateUser(){
          // Fetch user data
            const response = await fetch(`http://localhost:8000/spotify_data/updateuser`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "include",
            });

            if (!response.ok) {
                console.error("Failed to fetch SpotifyUser data");
                return;
            }

            let data = await response.json();
            data = data.spotify_user;
            console.log(data);
    }

    return (
        <div className="flex flex-col items-center p-6 space-y-6 min-h-screen justify-center">
            <Heading1 text={`${username} again? Yikes`} />

            <div className={"space-x-8"}>
            <Button text="Past Roasts" small={true} url="/history/" />
            <Button text={"Sign Out"} faded={true} small={true} method={handleLogoutClick}/>
            <Button text={"Delete Account"} faded={true} small={true} method={handleDeleteAccount}/>
            </div>

            <form className={"flex flex-col"} action="/wrapped/title/" method="POST">
                <div id="radio-group" className="flex flex-col items-start mt-8 ml-auto mr-auto">
                    <p>Choose a time range:</p>
                    <Radio
                        name="time_range"
                        value="short_term"
                        text="Past Month"
                        onChange={() => handleSelection(0)}
                        checked={timeframe === 0}
                    />
                    <Radio
                        name="time_range"
                        value="medium_term"
                        text="Past 6 Months"
                        onChange={() => handleSelection(1)}
                        checked={timeframe === 1}
                    />
                    <Radio
                        name="time_range"
                        value="long_term"
                        text="Past Year"
                        onChange={() => handleSelection(2)}
                        checked={timeframe === 2}
                    />
                </div>
                <Button text="Generate Roast" method={updateUser} extraClasses="mt-10 w-50 ml-auto mr-auto" />
            </form>

            {/* Separate form for navigating to a friend's profile */}
            <form onSubmit={handleSubmit} className="flex flex-grow flex-row items-center mt-2 mb-6">
                <input
                    name="other_user"
                    type="text"
                    placeholder="Enter Friend's Username"
                    className="lowercase p-2 border rounded mr-5"
                    value={otherUser}
                    onChange={(e) => setOtherUser(e.target.value)} // Update `otherUser` state
                />
                <Button text={"Generate Duo Roast"} method={() => null}/>

            </form>
            {popupMessage && (
                <div className="mt-4 p-4 bg-red-500 text-white rounded">
                    {popupMessage}
                </div>
            )}
        </div>
    );
}
