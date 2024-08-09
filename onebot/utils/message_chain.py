from typing import List, Union

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
        # elif isinstance(m, Audio):
        #     new_msg.append(MessageSegment.music(m.name))
        elif isinstance(m, Text):
            new_msg.append(MessageSegment.text(m.text))
        else:
            print(f"未知消息类型: {m}")
    return new_msg

def ms_unformat(msgs: List[MessageSegment]) -> List[Element]:
    new_elements: List[Element] = []
    for msg in msgs:
        if msg.type == "at":
            new_elements.append(At(uin=int(msg.data["qq"])))
        elif msg.type == "reply":
            new_elements.append(Quote(seq=int(msg.data["id"])))
        elif msg.type == "image":
            new_elements.append(Image(url=msg.data["file"]))
        # elif msg.type == "music":
        #     new_elements.append(Audio(name=msg.data["title"]))
        elif msg.type == "text":
            new_elements.append(Text(text=msg.data["text"]))
        else:
            print(f"未知消息类型: {msg}")
    return new_elements

def format(msg: List[str], type: Union[Element, MessageSegment]) -> List[Union[Element, MessageSegment]]:
    fm = []
    for m in msg:
        if type == MessageSegment:
            fm.append(MessageSegment(**m))
        elif type == Element:
            fm.append(Element(m))
    return fm

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