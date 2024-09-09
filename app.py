import asyncio

from lagrange.utils.log import install_loguru
from lagrange.client.events.service import ServerKick
from lagrange.client.client import Client
from lagrange import Lagrange, msg_push_handler, server_kick_handler, log

from lagrange.client.events.group import (
    GroupMessage,
    GroupRecall,
    GroupMemberQuit
)
from lagrange.client.events.friend import (
    FriendMessage
)

from onebot.handlers import (
    GroupMessageEventHandler,
    PrivateMessageEventHandler,
    GroupDecreaseEventHandler,
    GroupRecallEventHandler
)

from ws import connect
from config import Config, logger


class LagrangeOB11Client(Lagrange):
    def __init__(self, uin: int, sign_url: str):
        super().__init__(uin, sign_url=sign_url)

    async def run(self):
        with self.im as im:
            self.client = Client(self.uin, self.info, im.device, im.sig_info, self.sign, use_ipv6=Config.v6)
            for event, handler in self.events.items():
                self.client.events.subscribe(event, handler)
            self.client.push_deliver.subscribe("trpc.msg.olpush.OlPushService.MsgPush", msg_push_handler)
            self.client.push_deliver.subscribe("trpc.qq_new_tech.status_svc.StatusService.KickNT", server_kick_handler)
            self.client.connect()
            status = await self.login(self.client)
        if not status:
            log.login.error("Login failed")
            return
        await asyncio.create_task(connect(self.client))
        await self.client.wait_closed()


lag = LagrangeOB11Client(uin=Config.uin, sign_url=Config.sign_server)


async def handle_kick(client: "Client", event: "ServerKick"):
    logger.login.error(f"Kicked by Server: [{event.title}] {event.tips}")
    await client.stop()


lag.log.set_level(Config.log_level)
lag.subscribe(GroupMessage, GroupMessageEventHandler)
lag.subscribe(FriendMessage, PrivateMessageEventHandler)
lag.subscribe(GroupMemberQuit, GroupDecreaseEventHandler)
lag.subscribe(GroupRecall, GroupRecallEventHandler)
lag.subscribe(ServerKick, handle_kick)
