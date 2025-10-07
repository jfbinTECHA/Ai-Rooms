// WebSocket helpers

const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8001';

export class RoomWebSocket {
  private ws: WebSocket | null = null;
  private roomId: string;
  private onMessage: (message: any) => void;
  private onError: (error: Event) => void;

  constructor(roomId: string, onMessage: (message: any) => void, onError: (error: Event) => void) {
    this.roomId = roomId;
    this.onMessage = onMessage;
    this.onError = onError;
  }

  connect() {
    this.ws = new WebSocket(`${WS_BASE_URL}/ws/rooms/${this.roomId}`);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.onMessage(message);
    };

    this.ws.onerror = (error) => {
      this.onError(error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
    };
  }

  send(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}