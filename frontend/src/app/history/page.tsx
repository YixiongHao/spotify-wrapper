'use client';
import React, { useEffect, useState } from 'react';
import { useRouter } from "next/navigation";
import Heading1 from '../Components/Heading1';

export default function History() {
    const [history, setHistory] = useState<{ id: number, isDuo: boolean }[]>([]);
    const [popupMessage, setPopupMessage] = useState<string | null>(null);
    const [deleteId, setDeleteId] = useState<number | ''>(''); // State for the input box
    const router = useRouter();

    async function fetchSummary(): Promise<void> {
        try {
            const response = await fetch(`http://localhost:8000/spotify_data/displayhistory`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
            });

            if (!response.ok) {
                if (response.status === 500) {
                    setPopupMessage("No history for this account. Go create a roast!");
                } else {
                    console.error("Failed to fetch SpotifyUser data");
                }
                return;
            }
            const data = await response.json();
            console.log('Data fetched successfully:', data);
            setHistory(data); // Update state with the fetched data
        } catch (error) {
            console.error("Error fetching SpotifyUser data:", error);
        }
    }

    useEffect(() => {
        fetchSummary().catch(console.error);
    }, []);

    const handleButtonClick = (value: number) => {
        // Store the clicked value in localStorage
        localStorage.setItem('id', value.toString());
        localStorage.setItem('isDuo', 'false');

        // Redirect to another page
        router.push('/wrapped/title');
    };

    const handleDelete = async (): Promise<void> => {
        if (deleteId === '') {
            setPopupMessage("Please enter a valid ID.");
            return;
        }

        try {
            const response = await fetch(`http://localhost:8000/spotify_data/delete?deleteId=${deleteId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
            });

            if (!response.ok) {
                setPopupMessage(`Failed to delete item with ID ${deleteId}.`);
                return;
            }

            setPopupMessage(`Item with ID ${deleteId} deleted successfully.`);
            setDeleteId(''); // Clear the input box
            await fetchSummary(); // Refresh the list
        } catch (error) {
            console.error("Error deleting item:", error);
            setPopupMessage("An error occurred while trying to delete the item.");
        }
    };

    return (
        <>
            {/* Back Button */}
            <button
                onClick={() => router.push('/dashboard')}
                className="absolute top-4 right-4 px-4 py-2 bg-gray-300 text-black rounded hover:bg-gray-400"
            >
                Back
            </button>

            <Heading1 text="Past Roasts" />
            <p>Roast history information</p>
            <div className="flex flex-wrap gap-2 mt-4">
                {history.map((item, index) => (
                    <button
                        key={index}
                        onClick={() => handleButtonClick(item.id)}
                        className={`px-4 py-2 rounded text-white hover:opacity-90 ${
                            item.isDuo ? 'bg-green-500' : 'bg-blue-500'
                        }`}
                    >
                        {item.id}
                    </button>
                ))}
            </div>
            <div className="mt-4">
                <input
                    type="number"
                    value={deleteId}
                    onChange={(e) => setDeleteId(Number(e.target.value) || '')}
                    placeholder="Enter ID to delete"
                    className="px-2 py-1 border rounded mr-2"
                />
                <button
                    onClick={handleDelete}
                    className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                >
                    Delete
                </button>
            </div>
            {popupMessage && (
                <div className="mt-4 p-4 bg-red-500 text-white rounded">
                    {popupMessage}
                </div>
            )}
        </>
    );
}
