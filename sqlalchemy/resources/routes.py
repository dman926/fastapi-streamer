from fastapi import FastAPI
from .file import router as file_router
from .sockets import router as socket_router

routers = [
	file_router,
    socket_router
]

def initialize_routes(app: FastAPI) -> None:
    for router in routers:
        app.include_router(router)