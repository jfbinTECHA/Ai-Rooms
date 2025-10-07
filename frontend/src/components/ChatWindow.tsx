'use client';

import { useState, useEffect } from 'react';
import { fetchRoomMessages } from '@/lib/api';
import { RoomWebSocket } from '@/lib/ws';

interface Message {
  id: string;
  content: string;
  sender: string;
  timestamp: string;
}

interface ChatWindowProps {
  roomId: string;
}

export default function ChatWindow({ roomId }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [ws, setWs] = useState<RoomWebSocket | null>(null);

  useEffect(() => {
    // Fetch initial messages
    fetchRoomMessages(roomId)
      .then(data => setMessages(data))
      .catch(err => console.error('Failed to fetch messages', err));

    // Set up WebSocket for real-time updates
    const websocket = new RoomWebSocket(
      roomId,
      (message) => {
        setMessages(prev => [...prev, message]);
      },
      (error) => {
        console.error('WebSocket error', error);
      }
    );
    websocket.connect();
    setWs(websocket);

    return () => {
      websocket.disconnect();
    };
  }, [roomId]);

  return (
    <div className="flex-1 p-4 overflow-y-auto">
      <div className="space-y-4">
        {messages.map(message => (
          <div key={message.id} className="bg-white p-3 rounded-lg shadow">
            <div className="font-semibold">{message.sender}</div>
            <div className="text-gray-700">{message.content}</div>
            <div className="text-xs text-gray-500">{new Date(message.timestamp).toLocaleString()}</div>
          </div>
        ))}
      </div>
    </div>
  );
}