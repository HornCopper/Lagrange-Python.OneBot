from typing import List

from lagrange.client.message.elems import Text, Image, At, Audio, Quote, MarketFace
from lagrange.client.message.types import Element

from nonebot.adapters.onebot.v11.message import MessageSegment

def ms_format(msgs: List[Element]) -> List[MessageSegment]:
    new_msg: List[MessageSegment] = []
    for m in msgs:
        if isinstance(m, At):
            new_msg.append(MessageSegment.at(str(m.uin)))
        elif isinstance(m, Quote):
            new_msg.append(MessageSegment.reply(str(m.seq)))
        elif isinstance(m, (Image, MarketFace)):
            new_msg.append(MessageSegment.image(str(m.url)))
        elif isinstance(m, Audio):
            new_msg.append(MessageSegment.music(m.name))
        elif isinstance(m, Text):
            new_msg.append(MessageSegment.text(m.text))
        else:
            print(f"未知消息类型: {m}")
    return new_msg

def ctd(obj):
    if not hasattr(obj, "__dict__"):
        return obj
    
    result = {}
    for key, value in obj.__dict__.items():
        if hasattr(value, "__dict__"):
            result[key] = ctd(value)
        else:
            result[key] = value
    return result