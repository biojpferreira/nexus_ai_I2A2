import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ChatWindow } from './chat-window/chat-window';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  protected title = 'meu-chatbot';
}
