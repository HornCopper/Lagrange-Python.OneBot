from lagrange.client.events.group import GroupMessage
from lagrange.client.events.service import ServerKick
from lagrange.client.client import Client
from lagrange import Lagrange

from onebot.handlers import (
    GroupMessageEventHandler
)

from config import Config, logger

class LagrangeClient(Lagrange):
    def get_client(self):
        return self.client
    
lag = LagrangeClient(
    uin = Config.uin,
    protocol = Config.protocol,
    sign_url = Config.sign_server
)

async def handle_kick(client: "Client", event: "ServerKick"):
    logger.login.error(f"Kicked by Server: [{event.title}] {event.tips}")
    await client.stop()
        
lag.log.set_level(Config.log_level)
lag.subscribe(GroupMessage, GroupMessageEventHandler)
lag.subscribe(ServerKick, handle_kick)