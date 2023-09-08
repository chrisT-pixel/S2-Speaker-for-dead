import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';

@Injectable({
 providedIn: 'root',
})
export class WebSocketService {
  constructor(private socket: Socket) {}

  // Send a message to the server
  sendMessage(message: string): void {
    this.socket.emit('message', message);
  }

  // Receive messages from the server
  onMessage() {
    return this.socket.fromEvent<string>('message');
    
  }
}
