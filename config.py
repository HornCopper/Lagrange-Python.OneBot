import yaml
import os
from typing import Literal
from pydantic import BaseModel
from lagrange.utils.log import LoggerProvider, install_loguru

logger = LoggerProvider()

install_loguru()

class config(BaseModel):
    uin: int = 0
    protocol: Literal["windows", "macos", "linux"] = "linux"
    sign_server: str = ""
    ws_url: str = ""
    http_host: str = ""
    http_port: str = ""
    log_level: str = "INFO"
    v6: bool = False
    ignore_self: bool = True


def yaml_to_class(yaml_str, cls):
    config_data = yaml.safe_load(yaml_str)
    return cls(**config_data)


script_dir = os.path.dirname(os.path.abspath(__file__))
yaml_file_path = os.path.join(script_dir, "config.yml")

with open(yaml_file_path, "r", encoding="utf-8") as f:
    Config = yaml_to_class(f.read(), config)