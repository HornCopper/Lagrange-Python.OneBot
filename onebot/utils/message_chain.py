from typing import List, Union, Literal

from lagrange.client.message.elems import Text, Image, At, Quote, MarketFace, Audio
from lagrange.client.message.types import Element
from lagrange.client.client import Client

from onebot.utils.message_segment import MessageSegment
from onebot.utils.audio import mp3_to_silk

import io
import httpx
import urllib
import os
import base64

from config import logger

class MessageConverter:
    def __init__(self, client: Client):
        self.client = client

    async def convert_to_segments(self, elements: List[Element], message_type: Literal["grp", "friend"], group_id: int = 0, uid: str = "") -> List[MessageSegment]:
        """
        将 Lagrange.Element 列表转换为 MessageSegment 列表
        将 Lagrange 传入的消息转换为 OneBot 处理端接受的数据类型
        """
        segments: List[MessageSegment] = []
        for element in elements:
            if isinstance(element, At):
                segments.append(MessageSegment.at(str(element.uin)))
            elif isinstance(element, Quote):
                segments.append(MessageSegment.reply(str(element.seq)))
            elif isinstance(element, (Image, MarketFace)):
                segments.append(MessageSegment.image(str(element.url)))
            elif isinstance(element, Audio):
                # RIP: wyapx 呜呜呜呜
                if message_type == "grp":
                    url = await self.client._highway.get_audio_down_url(element, gid=group_id)
                elif message_type == "friend":
                    url = await self.client._highway.get_audio_down_url(element, uid=uid)
                segments.append(MessageSegment.record(file=url))
            elif isinstance(element, Text):
                segments.append(MessageSegment.text(element.text))
            else:
                logger.onebot.error(f"Unknown message type: {element}")
        return segments

    async def convert_to_elements(self, segments: List[MessageSegment], group_id: int = 0, uid: str = "") -> List[Element]:
        """
        将 MessageSegment 列表转换为 Lagrange.Element 列表
        将 OneBot 处理端 收到的消息转换为 Lagrange 接受的数据类型
        """
        elements: List[Element] = []
        for segment in segments:
            if segment.type == "at":
                elements.append(At(uin=int(segment.data["qq"])))
            elif segment.type == "reply":
                elements.append(Quote(seq=int(segment.data["id"])))
            elif segment.type == "image":
                image_content = segment.data["file"]
                image_content = await self._process_image_content(image_content)
                if image_content:
                    if group_id:
                        elements.append(await self.client.upload_grp_image(image_content, group_id))
                    elif uid:
                        elements.append(await self.client.upload_friend_image(image_content, uid=uid))
            elif segment.type == "record":
                voice_content = segment.data["file"]
                voice_content = await self._process_voice_content(voice_content)
                if voice_content:
                    voice_content_silk = await mp3_to_silk(voice_content)
                    if group_id:
                        elements.append(await self.client.upload_grp_audio(voice_content_silk, group_id))
                    elif uid:
                        elements.append(await self.client.upload_friend_audio(voice_content_silk, uid=uid))
            elif segment.type == "text":
                elements.append(Text(text=segment.data["text"]))
            else:
                logger.onebot.error(f"Unknown message type: {segment}")
        return elements

    def parse_message(self, messages: List[str], target_type: Union[Element, MessageSegment]) -> List[Union[Element, MessageSegment]]:
        parsed_messages = []
        for message in messages:
            if target_type == MessageSegment:
                parsed_messages.append(MessageSegment(**message))
            elif target_type == Element:
                parsed_messages.append(Element(message))
        return parsed_messages

    def convert_to_dict(self, obj):
        if not hasattr(obj, "__dict__"):
            return obj
        
        result = {}
        for key, value in obj.__dict__.items():
            result[key] = self.convert_to_dict(value) if hasattr(value, "__dict__") else value
        return result

    async def _process_image_content(self, content: Union[str, bytes, io.BytesIO]) -> io.BytesIO:
        if isinstance(content, (bytes, io.BytesIO)):
            return io.BytesIO(content)
        elif isinstance(content, str):
            if content.startswith("http"):
                return await self._download_image_content(content)
            elif content.startswith("file"):
                return self._load_local_image_content(content)
            elif content.startswith("base64"):
                return io.BytesIO(base64.b64decode(content[9:]))
            else:
                raise ValueError(f"Unknown content type for Image {content}!")
        else:
            raise ValueError(f"Unknown file type for Image {content}!")
        
    async def _download_image_content(self, url: str) -> io.BytesIO:
        async with httpx.AsyncClient(follow_redirects=True, verify=False) as httpx_client:
            try:
                response = await httpx_client.get(url, timeout=600)
                return io.BytesIO(response.content)
            except httpx.TimeoutException:
                logger.onebot.error(f"Image download timed out: {url}")
                return None

    def _load_local_image_content(self, file_path: str) -> io.BytesIO:
        local_path = urllib.parse.urlparse(file_path).path
        if local_path.startswith("/") and local_path[2] == ":":
            local_path = local_path[1:]
        if os.path.exists(local_path):
            with open(local_path, "rb") as file:
                return io.BytesIO(file.read())
        else:
            logger.onebot.error(f"Local image not found: {local_path}")
            return None

    async def _process_voice_content(self, content: Union[str, bytes, io.BytesIO]) -> io.BytesIO:
        if isinstance(content, (bytes, io.BytesIO)):
            return io.BytesIO(content)
        elif isinstance(content, str):
            if content.startswith("http"):
                return await self._download_voice_content(content)
            elif content.startswith("file"):
                return self._load_local_voice_content(content)
            elif content.startswith("base64"):
                return io.BytesIO(base64.b64decode(content[9:]))
            else:
                raise ValueError(f"Unknown content type for Voice {content}!")
        else:
            raise ValueError(f"Unknown file type for Voice {content}!")

    async def _download_voice_content(self, url: str) -> io.BytesIO:
        async with httpx.AsyncClient(follow_redirects=True, verify=False) as httpx_client:
            try:
                response = await httpx_client.get(url, timeout=600)
                return io.BytesIO(response.content)
            except httpx.TimeoutException:
                logger.error(f"Voice download timed out: {url}")
                return None

    def _load_local_voice_content(self, file_path: str) -> io.BytesIO:
        local_path = urllib.parse.urlparse(file_path).path
        if local_path.startswith("/") and local_path[2] == ":":
            local_path = local_path[1:]
        if os.path.exists(local_path):
            with open(local_path, "rb") as file:
                return io.BytesIO(file.read())
        else:
            logger.error(f"Local voice not found: {local_path}")
            return None