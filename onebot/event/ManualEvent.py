from pydantic import BaseModel
from typing import Literal
from datetime import datetime

from config import Config

class Event(BaseModel):
    time: int = int(datetime.now().timestamp())
    self_id: int = Config.uin
    post_type: Literal["message", "notice", "request", "meta_event"] = ""

class Sender(BaseModel):
    user_id: int = 0
    nickname: str = ""
    sex: Literal["male", "female", "unknown"] = "unknown"
    age: int = 0

class Anonymous(BaseModel):
    id: int = 0
    name: str = ""
    flag: str = ""