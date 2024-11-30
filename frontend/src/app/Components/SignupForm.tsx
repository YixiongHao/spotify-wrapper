import { useRouter } from 'next/navigation';
import React, { useState, useEffect, ChangeEvent, FormEvent } from 'react';
import { logError } from '../utils/logger';
import { logInfo } from '../utils/logger';
import login from '../login/page';

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
        fetch('https://wrapped-backend.fly.dev/spotify/get-csrf-token/', {
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'Origin': 'https://wrapped-backend.fly.dev'
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
            //const response = await fetch('http://localhost:8000/spotify/register/', {
            const response = await fetch('https://wrapped-backend.fly.dev/spotify/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken || '',
                    'Accept': 'application/json',
                    'Origin': 'https://wrapped-backend.fly.dev'
                },
                body: new URLSearchParams({
                    username: formData.username,
                    email: formData.email,
                    password1: formData.password1,
                    password2: formData.password2,
                }),
                credentials: 'include',
            });

            
            // Log the full response details
            logInfo('Response status:', response.status);
            const responseText = await response.text();
            logInfo('Raw response:', responseText);

            try {
                const data = JSON.parse(responseText);
                
                if (response.ok) {
                    logInfo('Sign-Up Successful:', data);
                    setErrorMessage(null);
                    router.push('dashboard/');
                } else {
                    // Log the full error response
                    logError('Server Error Response:', {
                        status: response.status,
                        statusText: response.statusText,
                        data: data,
                        errors: data.errors
                    });

                    if (data.errors) {
                        const errorMessages = typeof data.errors === 'string'
                            ? data.errors
                            : Object.values(data.errors)
                                .flat()
                                .join(' ');
                        setErrorMessage(errorMessages);
                    } else {
                        setErrorMessage('Unexpected Error. Try Again');
                    }
                }
            } catch (parseError) {
                logError('Error parsing JSON response:', {
                    parseError,
                    rawResponse: responseText
                });
                setErrorMessage('Error parsing server response');
            }
        } catch (error) {
            logError('Network/Fetch Error:', {
                error,
                requestData: {
                    url: 'https://wrapped-backend.fly.dev/spotify/register/',
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept': 'application/json',
                        'Origin': 'https://wrapped-backend.fly.dev'
                    },
                }
            });
            setErrorMessage('An Unexpected Error Occurred. Please try again.');
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <div>
                <label>Username:</label>
                <input type="text" name="username" value={formData.username} onChange={handleChange} />
            </div>
            <div>
                <label>Email:</label>
                <input type="text" name="email" value={formData.email} onChange={handleChange} />
            </div>
            <div>
                <label>Password:</label>
                <input type="password" name="password1" value={formData.password1} onChange={handleChange} />
            </div>
            <div>
                <label>Retype Password:</label>
                <input type="password" name="password2" value={formData.password2} onChange={handleChange} />
            </div>
            <button type="submit">Sign Up!</button>
            {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}
        </form>
    )
}

export default SignupForm;
