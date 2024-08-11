import os
import asyncio

config_default = """# Lagrange Python (OneBot V11) Configuration

uin: ""
# Bot QQ号 使用扫码登录

protocal: ""
# 登录协议 推荐使用Linux（默认）

sign_server: ""
# SignServer 地址 不可使用`Android`的`QSign`

ws_url: ""
# 反向 WebSocket 地址
"""

if not os.path.exists("./config.yml"):
    print("The configuration file does not exist, please edit it, it has been created for you in current directory.")
    with open("./config.yml", "w", encoding="utf8") as f:
        f.write(config_default)
    os._exit(0)

from ws import connect
from app import lag

async def main():
    task_lgr = asyncio.create_task(lag.run())
    task_ws = asyncio.create_task(connect())
    
    await asyncio.gather(task_lgr, task_ws)

asyncio.run(main())