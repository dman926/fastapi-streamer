import { Component, OnDestroy, OnInit } from '@angular/core';
import { Subscription, retry } from 'rxjs';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';

@Component({
	selector: 'app-root',
	templateUrl: './app.component.html',
	styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit, OnDestroy {
	title = 'test-client';

	private socket: WebSocketSubject<any> | undefined; // If you have an interface for incoming websocket data, you can replace <any> with <INTERFACE>
	private socketSub: Subscription | undefined;

	ngOnInit(): void {
		this.socket = webSocket('ws://localhost:8000/'); // Open a new websocket connection
		// Subscribe to incoming data. Retry the connection if it closes.
		this.socket.pipe(retry()).subscribe(payload => {
			console.log(payload); // Print out incoming data
		});
		this.socket.next('ping'); // Send a string
	}

	ngOnDestroy(): void {
		this.socketSub?.unsubscribe();
		this.socket?.unsubscribe(); // Close the connection
	}
}
