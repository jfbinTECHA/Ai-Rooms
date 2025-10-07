// REST API helpers

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchRooms() {
  const response = await fetch(`${API_BASE_URL}/api/v1/rooms`);
  if (!response.ok) {
    throw new Error('Failed to fetch rooms');
  }
  return response.json();
}

export async function fetchRoomMessages(roomId: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/rooms/${roomId}/messages`);
  if (!response.ok) {
    throw new Error('Failed to fetch messages');
  }
  return response.json();
}

export async function sendMessage(roomId: string, content: string, sender: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/rooms/${roomId}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ content, sender }),
  });
  if (!response.ok) {
    throw new Error('Failed to send message');
  }
  return response.json();
}

export async function createRoom(name: string, description?: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/rooms`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name, description }),
  });
  if (!response.ok) {
    throw new Error('Failed to create room');
  }
  return response.json();
}