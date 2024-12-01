import { useRouter } from 'next/navigation';
import React, { useState, useEffect, ChangeEvent, FormEvent } from 'react';
import { logError } from '../utils/logger';
import { logInfo } from '../utils/logger';
import Input from "@/app/Components/Input";
import Button from "@/app/Components/Button";

interface FormData {
    username: string
    email: string
    password1: string
    password2: string
}

const getCookie = (name: string): string | null => {
    const cookieValue = document.cookie.split('; ')
        .find((row) => row.startsWith(name + '='))?.split('=')[1];
    return cookieValue ? decodeURIComponent(cookieValue) : null;
};

const SignupForm: React.FC = () => {
    const [formData, setFormData] = useState<FormData>({
        username: '',
        email: '',
        password1: '',
        password2: ''
    });
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const router = useRouter()

    useEffect(() => {
        //fetch('http://localhost:8000/spotify/get-csrf-token/', {
        fetch('https://spotify-wrapped-backend.vercel.app/spotify/get-csrf-token/', {
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'Origin': 'https://spotify-wrapped-frontend.vercel.app'
            },
        })
        .then((response) => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
        })
        .catch((error) => {
            logError('Error fetching CSRF token::', error);
        });
    }, []);

    const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value});
    };

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        const csrfToken = getCookie('csrftoken');
    
        try {
            logInfo('Attempting signup with data:', {
                username: formData.username,
                email: formData.email,
                // Don't log passwords
            });
    
            const response = await fetch('https://spotify-wrapped-backend.vercel.app/spotify/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken || '',
                    'Accept': 'application/json',
                    'Origin': 'https://spotify-wrapped-frontend.vercel.app'
                },
                body: new URLSearchParams({
                    username: formData.username,
                    email: formData.email,
                    password1: formData.password1,
                    password2: formData.password2,
                }),
                credentials: 'include',
            });
    
            const responseText = await response.text();
            logInfo('Raw response:', responseText);
    
            try {
                const data = JSON.parse(responseText);
                
                if (response.ok) {
                    logInfo('Sign-Up Successful:', data);
                    setErrorMessage(null);
                    router.push('dashboard/');
                } else {
                    logError('Server Error:', {
                        status: response.status,
                        statusText: response.statusText,
                        data: data,
                        details: data.details,  // From our enhanced error response
                        trace: data.trace       // From our enhanced error response
                    });
    
                    setErrorMessage(data.error || 'An unexpected error occurred');
                }
            } catch (parseError) {
                logError('Error parsing response:', {
                    parseError,
                    rawResponse: responseText
                });
            }
        } catch (error) {
            logError('Network/Fetch Error:', error);
            setErrorMessage('An unexpected error occurred. Please try again.');
        }
    };

    return (
        <form onSubmit={handleSubmit} className={"mt-5"}>
            <Input label={"Username:"} type={"text"} name={"username"} value={formData.username} onChange={handleChange}/>
            <Input label={"Email:"} type={"text"} name={"email"} value={formData.email} onChange={handleChange}/>
            <Input label={"Password:"} type={"password"} name={"password1"} value={formData.password1} onChange={handleChange}/>
            <Input label={"Retype Password:"} type={"password"} name={"password2"} value={formData.password2} onChange={handleChange}/>
            <p className={"text-red-600"}>{errorMessage}</p>
            <div className={"w-full flex"}>
            <Button text={"Sign Up!"} method={() => null} extraClasses={"mt-2 mr-auto ml-auto"}/>
            </div>
        </form>
    )
}

export default SignupForm;
