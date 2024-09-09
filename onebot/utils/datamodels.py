from packaging.version import parse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

import pydantic

class LagrangeModel(BaseModel):
    TABLE_NAME: Optional[str] = None
    id: Optional[int] = None

    def dump(self, *args, **kwargs):
        if parse(pydantic.__version__) < parse("2.0.0"):
            return self.dict(*args, **kwargs)
        else:
            return self.model_dump(*args, **kwargs)
        
class MessageEvent(LagrangeModel):
    TABLE_NAME: Optional[str] = "MessageEvent"
    msg_id: int = 0
    uid: str = ""
    seq: int = 0
    time: int = int(datetime.now().timestamp())
    rand: int = 0
    grp_id: int = 0
    uin: int = 0
    grp_name: str = ""
    nickname: str = ""
    msg: str = ""
    msg_chain: list = []

class RequestEvent(LagrangeModel):
    TABLE_NAME: Optional[str] = "RequestEvent"
    seq: int = 0
    event_type: int = 0
    state: Optional[int] = 0
    group: Optional[int] = 0
    uid: Optional[str] = ""
    invitor_uid: Optional[str] = ""
    # invitor: Optional[RspUser] = proto_field(6, default=None)
    # operator: Optional[RspUser] = proto_field(7, default=None)
    # comment: str = proto_field(9, default="")