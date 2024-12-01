"use client";
import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { logError } from './utils/logger';
import Button from './Components/Button';

export default function Home() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
  const checkAuthentication = async () => {
    try {
      const response = await fetch('https://spotify-wrapped-backend.vercel.app/spotify/is-authenticated/', {
        credentials: 'include'
      });
      const data = await response.json();

      if (data.status) {
        router.push('/dashboard');
      } else {
        setIsAuthenticated(false);
      }
    } catch (error) {
        logError('Error:', error);
    }
  };

  checkAuthentication();
  }, [router]);

  const handleLoginClick = () => {
    router.push('/login');
  };

  if (isAuthenticated) {
    return null; // or a loading spinner
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-7xl font-bold mb-4 text-black">spotify roaster</h1>
      <h2 className="text-4xl mb-8 text-black">your music taste has never been so embarrassing</h2>
      <Button text = "login" method = {handleLoginClick}/>
    </div>
  );
}
