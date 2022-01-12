from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Optional
import base64
import os

router = APIRouter(
    tags=['Sockets']
)

class WebSocketConnection:
	def __init__(self, sid: str, socket: WebSocket):
		self.sid = sid
		self.socket = socket

class ConnectionManager:
	def __init__(self):
		self.active_connections: list[WebSocketConnection] = []

	async def connect(self, websocket: WebSocket) -> str:
		await websocket.accept()
		sid = ''
		do = True
		while do:
			do = False
			sid = base64.b32encode(os.urandom(32)).decode('utf8')
			for connection in self.active_connections:
				if connection.sid == sid:
					do = True
					break
		self.active_connections.append(WebSocketConnection(sid=sid, socket=websocket))
		return sid

	def disconnect(self, websocket: WebSocket) -> None:
		for i in range(len(self.active_connections)):
			if self.active_connections[i].socket == websocket:
				self.active_connections.pop(i)
				break
	
	async def send_message(self, message: dict, websocket: WebSocket) -> None:
		await websocket.send_json(message)

	async def broadcast(self, message: dict) -> None:
		for connection in self.active_connections:
			await connection.send_json(message)

	def get_socket_from_sid(self, sid: str) -> Optional[WebSocket]:
		for connection in self.active_connections:
			if connection.sid == sid:
				return connection.socket

root_manager = ConnectionManager()

@router.websocket('/')
async def root_socket(websocket: WebSocket):
	sid = await root_manager.connect(websocket)
	await root_manager.send_message({'sid': sid}, websocket)
	print('Client connected')
	try:
		while True:
			print(await websocket.receive_text())
			await root_manager.send_message({'pong': True}, websocket)
	except WebSocketDisconnect:
		root_manager.disconnect(websocket)
		print('Client disconnected')