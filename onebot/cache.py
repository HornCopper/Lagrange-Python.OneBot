from typing import Union, Optional

from onebot.utils.database import db
from onebot.utils.datamodels import MessageEvent

def get_info(info: Union[str, int]) -> Optional[Union[str, int]]:
    if isinstance(info, str):
        msg_event = db.where_all(MessageEvent())
        for each_msg in msg_event:
            each_msg: MessageEvent
            if each_msg.uid == info:
                return each_msg.uin
    if isinstance(info, int):
        msg_event = db.where_all(MessageEvent())
        for each_msg in msg_event:
            each_msg: MessageEvent
            if each_msg.uin == info:
                return each_msg.uid
    return None