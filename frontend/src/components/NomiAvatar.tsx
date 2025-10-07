'use client';

import { useState, useEffect } from 'react';

export default function NomiAvatar() {
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    // Simulate animation on message
    const interval = setInterval(() => {
      setIsAnimating(true);
      setTimeout(() => setIsAnimating(false), 1000);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="text-center">
      <div className={`w-32 h-32 mx-auto bg-indigo-500 rounded-full flex items-center justify-center text-white text-4xl font-bold transition-transform ${isAnimating ? 'scale-110' : 'scale-100'}`}>
        N
      </div>
      <h3 className="mt-4 text-lg font-semibold">Nomi</h3>
      <p className="text-gray-600">AI Assistant</p>
    </div>
  );
}