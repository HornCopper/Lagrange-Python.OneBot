from fastapi import FastAPI, Request, Depends

from lagrange.client.events.service import ServerKick
from lagrange.client.client import Client
from lagrange import Lagrange, log

from lagrange.client.events.group import (
    GroupMessage,
    GroupRecall,
    GroupMemberQuit,
    GroupInvite,
    GroupMemberJoinRequest,
    GroupMuteMember,
    GroupNudge,
    GroupMemberJoined,
    GroupMemberJoinedByInvite,
    GroupAdminChange
)
from lagrange.client.events.friend import (
    FriendMessage,
    FriendRecall,
    FriendRequest,
    FriendDeleted
)

from onebot.communications.api import OneBotAPI_V11
from onebot.handlers import (
    GroupMessageEventHandler,
    PrivateMessageEventHandler,
    GroupDecreaseEventHandler,
    GroupRecallEventHandler,
    GroupRequestEventHandler,
    FriendRecallEventHandler,
    GroupBanEventHandler,
    FriendRequestEventHandler,
    FriendDeletedEventHandler,
    GroupPokeNotifyEventHandler,
    GroupIncreaseEventHandler,
    GroupAdminEventHandler
)
from onebot.utils.database import db
from onebot.utils.datamodels import UserInformation
from onebot.utils.functions import get_params

from ws import connect
from config import Config, logger

import asyncio
import uvicorn

from typing import Union

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

async def run_fastapi(app: OneBotAPI, client: Client):
    if Config.http_get_host == "NO":
        return
    app.set_client(client)
    config = uvicorn.Config(app, host=Config.http_get_host, port=int(Config.http_get_port), log_level="critical")
    logger.onebot.success(f"HTTP Server launched! Listening at http://{Config.http_get_host}:{Config.http_get_port}!")
    server = uvicorn.Server(config)
    await server.serve()

async def update_friend_data(client: Client):
    friend_list_data = await client.get_friend_list()
    for each_friend in friend_list_data:
        if db.where_one(UserInformation(), "uin = ?", each_friend.uin, default=None) is not None:
            continue
        db.save(UserInformation(uin=each_friend.uin, uid=each_friend.uid))

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


class LagrangeOB11Client(Lagrange):
    def __init__(self, uin: int, sign_url: str):
        super().__init__(uin, sign_url=sign_url)

    async def run(self):
        with self.im as im:
            self.client = Client(self.uin, self.info, im.device, im.sig_info, self.sign, use_ipv6=Config.v6)
            for event, handler in self.events.items():
                self.client.events.subscribe(event, handler)
            self.client.connect()
            status = await self.login(self.client)
        if not status:
            log.login.error("Login failed")
            return
        await update_friend_data(self.client)
        await asyncio.gather(
            connect(self.client),
            run_fastapi(OneBotHTTPServer, self.client)
        )
        await self.client.wait_closed()


lag = LagrangeOB11Client(uin=Config.uin, sign_url=Config.sign_server)


async def handle_kick(client: "Client", event: "ServerKick"):
    logger.login.error(f"Kicked by Server: [{event.title}] {event.tips}")
    await client.stop()


lag.log.set_level(Config.log_level)

# GroupEvent
lag.subscribe(GroupMessage, GroupMessageEventHandler)
lag.subscribe(GroupNudge, GroupPokeNotifyEventHandler)
lag.subscribe(GroupMemberJoined, GroupIncreaseEventHandler)
lag.subscribe(GroupMemberJoinedByInvite, GroupIncreaseEventHandler)
lag.subscribe(GroupMemberQuit, GroupDecreaseEventHandler)
lag.subscribe(GroupRecall, GroupRecallEventHandler)
lag.subscribe(GroupInvite, GroupRequestEventHandler)
lag.subscribe(GroupMemberJoinRequest, GroupRequestEventHandler)
lag.subscribe(GroupMuteMember, GroupBanEventHandler)
lag.subscribe(GroupAdminChange, GroupAdminEventHandler)

# Friend Event
lag.subscribe(FriendRecall, FriendRecallEventHandler)
lag.subscribe(FriendRequest, FriendRequestEventHandler)
lag.subscribe(FriendDeleted, FriendDeletedEventHandler)
lag.subscribe(FriendMessage, PrivateMessageEventHandler)
lag.subscribe(ServerKick, handle_kick)
