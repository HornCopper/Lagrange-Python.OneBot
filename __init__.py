import os
import sys
import asyncio

with open("./config_template.yml", encoding="utf-8", mode="r") as default:
    config_default = default.read()

if not os.path.exists("./config.yml"):
    print("The configuration file does not exist, please edit it, it has been created for you in current directory.\nDo not edit `config_template.yml`, `config.yml` instead!")
    with open("./config.yml", "w", encoding="utf8") as f:
        f.write(config_default)
    sys.exit(0)

from app import lag


async def main():
    await asyncio.create_task(lag.run())


asyncio.run(main())
