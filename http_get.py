from typing import Union
from fastapi import FastAPI, Request, Depends

from lagrange.client.client import Client

from onebot.communications.api import OneBotAPI_V11
from onebot.utils.functions import get_params

from config import Config, logger

import uvicorn

class OneBotAPI(FastAPI):
    def __init__(self, client: Union[Client, None] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client

    def set_client(self, client: Client):
        self.client = client

    async def inject_client(self):
        if self.client is None:
            raise ValueError("Lagrange is not initialized!")
        return self.client

async def get_client(app: OneBotAPI = Depends()):
    return await app.inject_client()

async def http_get(app: OneBotAPI, client: Client):
    if Config.http_get_host == "" or Config.http_get_port == "":
        return
    app.set_client(client)
    config = uvicorn.Config(app, host=Config.http_get_host, port=int(Config.http_get_port), log_level="critical")
    logger.onebot.success(f"HTTP Server launched! Listening at http://{Config.http_get_host}:{Config.http_get_port}!")
    server = uvicorn.Server(config)
    await server.serve()

OneBotHTTPServer = OneBotAPI()

@OneBotHTTPServer.get("/{path:path}")
async def _(request: Request, path: str = ""):
    client = await OneBotHTTPServer.inject_client()
    instance = OneBotAPI_V11(client)
    echo = request.query_params.get("echo", None)
    if not hasattr(instance, path):
        return {"status": "failed", "code": 404, "data": None, "echo": echo}
    else:
        method = getattr(instance, path)
        try:
            result = await method(**get_params(method, dict(request.query_params)))
        except Exception as e:
            logger.onebot.error(f"HTTP API Request Failed: `{path}`: {dict(request.query_params)}. ({e})")
            return {"status": "failed", "code": -1, "data": None, "echo": echo}
        logger.onebot.success(f"HTTP API Request Successfully: `{path}`: {dict(request.query_params)}.")
        return result
