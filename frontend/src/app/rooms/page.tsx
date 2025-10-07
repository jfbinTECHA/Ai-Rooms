'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import RoomList from '@/components/RoomList';
import TopBar from '@/components/TopBar';

export default function RoomsPage() {
  return (
    <div className="min-h-screen bg-gray-100">
      <TopBar />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">Rooms</h1>
        <RoomList />
        <div className="mt-6">
          <Link
            href="/"
            className="bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700"
          >
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}