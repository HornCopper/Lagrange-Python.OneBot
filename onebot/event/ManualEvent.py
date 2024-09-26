from pydantic import BaseModel
from typing import Literal
from datetime import datetime

class Event(BaseModel):
    time: int = 0
    self_id: int = 0
    post_type: Literal["message", "notice", "request", "meta_event"] = "message"

class Sender(BaseModel):
    user_id: int = 0
    nickname: str = ""
    sex: Literal["male", "female", "unknown"] = "unknown"
    age: int = 0

class Anonymous(BaseModel):
    id: int = 0
    name: str = ""
    flag: str = ""