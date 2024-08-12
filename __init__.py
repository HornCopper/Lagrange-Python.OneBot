import os
import sys
import asyncio

config_default = """# Lagrange Python (OneBot V11) Configuration

uin: ""
# Bot QQ号 使用扫码登录

protocol: ""
# 登录协议 推荐使用Linux（默认）

sign_server: ""
# SignServer 地址 不可使用`Android`的`QSign`

ws_url: ""
# 反向 WebSocket 地址

log_level: "INFO"
"""

if not os.path.exists("./config.yml"):
    print("The configuration file does not exist, please edit it, it has been created for you in current directory.")
    with open("./config.yml", "w", encoding="utf8") as f:
        f.write(config_default)
    sys.exit(0)

from app import lag


async def main():
    await asyncio.create_task(lag.run())


asyncio.run(main())
