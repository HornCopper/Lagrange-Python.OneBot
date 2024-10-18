from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

from lagrange.client.client import Client

from reserved_websocket import websocket_process
from http_get import OneBotAPI
from config import Config, logger

from onebot.communications.api import OneBotAPI_V11

import uvicorn
import json

class WebSocketManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

forward_websocket_manager = WebSocketManager()

OneBotWSServer = OneBotAPI()

@OneBotWSServer.websocket("/forward")
async def websocket_endpoint(websocket: WebSocket):
    await forward_websocket_manager.connect(websocket)
    client = await OneBotWSServer.inject_client()
    instance = OneBotAPI_V11(client)
    await forward_websocket_manager.send_personal_message(
        json.dumps(
            {
                "time": int(datetime.now().timestamp()),
                "self_id": client.uin,
                "post_type": "meta_event",
                "meta_event_type": "lifecycle",
                "sub_type": "connect"
            }
        ),
        websocket
    )
    try:
        while True:
            rec = await websocket.receive_text()
            rec = json.loads(rec)
            rply = await websocket_process(client, rec, instance)
            await forward_websocket_manager.send_personal_message(json.dumps(rply, ensure_ascii=False), websocket)
    except WebSocketDisconnect:
        forward_websocket_manager.disconnect(websocket)
        logger.onebot.warning("Forward websocket disconnected!")

async def forward_websocket_connect(client: Client):
    if Config.forward_ws_host == "" or Config.forward_ws_port == "":
        return
    OneBotWSServer.set_client(client)
    config = uvicorn.Config(
        OneBotWSServer,
        host=Config.forward_ws_host,
        port=int(Config.forward_ws_port),
        log_level="critical"
    )
    server = uvicorn.Server(config)
    logger.onebot.success(f"Forward websocket launched! Listening at ws://{Config.forward_ws_host}:{Config.forward_ws_port}/forward")
    await server.serve()
