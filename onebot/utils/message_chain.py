from typing import List, Union

from lagrange.client.message.elems import Text, Image, At, Audio, Quote, MarketFace
from lagrange.client.message.types import Element
from lagrange.client.client import Client

from nonebot.adapters.onebot.v11.message import MessageSegment

import io
import httpx
import urllib
import os

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

async def ms_unformat(client: Client, msgs: List[MessageSegment], group_id: int = 0, uid: str = "") -> List[Element]:
    new_elements: List[Element] = []
    for msg in msgs:
        if msg.type == "at":
            new_elements.append(At(uin=int(msg.data["qq"])))
        elif msg.type == "reply":
            new_elements.append(Quote(seq=int(msg.data["id"])))
        elif msg.type == "image":
            img_raw = msg.data["file"]
            if isinstance(img_raw, (bytes, io.BytesIO)):
                img_raw = io.BytesIO(img_raw)
            elif isinstance(img_raw, str):
                if img_raw[0:4] == "http":
                    async with httpx.AsyncClient(follow_redirects=True, verify=False) as httpx_client:
                        try:
                            resp = await httpx_client.get(img_raw, timeout=600)
                            result = resp.content
                            img_raw = io.BytesIO(result)
                        except httpx.TimeoutException:
                            continue
                elif img_raw[0:4] == "file":
                    local_path = urllib.parse.urlparse(img_raw).path
                    if local_path.startswith("/") and local_path[2] == ":":
                        local_path = local_path[1:]
                    print(local_path)
                    if not os.path.exists(local_path):
                        continue
                    print(1)
                    with open(local_path, "rb") as f:
                        img_raw = io.BytesIO(f.read())
                else:
                    raise ValueError(f"Unknown content type of Image `{img_raw}`!")
            else:
                raise ValueError(f"Unknown file type of Image `{img_raw}`!")
            if group_id:
                new_elements.append(await client.upload_grp_image(img_raw, group_id))
            elif uid != "":
                new_elements.append(await client.upload_friend_image(img_raw, uid=uid))
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