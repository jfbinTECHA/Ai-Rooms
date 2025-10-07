'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { fetchRooms } from '@/lib/api';

interface Room {
  id: string;
  name: string;
  description?: string;
}

export default function RoomList() {
  const [rooms, setRooms] = useState<Room[]>([]);

  useEffect(() => {
    fetchRooms()
      .then(data => setRooms(data))
      .catch(err => console.error('Failed to fetch rooms', err));
  }, []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {rooms.map(room => (
        <div key={room.id} className="bg-white p-4 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-2">{room.name}</h2>
          <p className="text-gray-600 mb-4">{room.description || 'No description'}</p>
          <Link
            href={`/chat/${room.id}`}
            className="bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700"
          >
            Enter Room
          </Link>
        </div>
      ))}
    </div>
  );
}