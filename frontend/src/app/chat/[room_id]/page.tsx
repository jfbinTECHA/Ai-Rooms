'use client';

import { useParams } from 'next/navigation';
import ChatWindow from '@/components/ChatWindow';
import InputBar from '@/components/InputBar';
import NomiAvatar from '@/components/NomiAvatar';
import TopBar from '@/components/TopBar';

export default function ChatPage() {
  const params = useParams();
  const roomId = params.room_id as string;

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <TopBar />
      <div className="flex-1 flex">
        <div className="flex-1 flex flex-col">
          <ChatWindow roomId={roomId} />
          <InputBar roomId={roomId} />
        </div>
        <div className="w-64 bg-white shadow-md p-4">
          <NomiAvatar />
        </div>
      </div>
    </div>
  );
}