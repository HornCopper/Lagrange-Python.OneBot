import re

from base64 import b64encode
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, Union, Optional, Iterable, Tuple
from typing_extensions import Self

def b2s(b: Optional[bool]) -> str | None:
    """转换布尔值为字符串。"""
    return b if b is None else str(b).lower()


def f2s(file: Union[str, bytes, BytesIO, Path]) -> str:
    if isinstance(file, BytesIO):
        file = file.getvalue()
    if isinstance(file, bytes):
        file = f"base64://{b64encode(file).decode()}"
    elif isinstance(file, Path):
        file = file.resolve().as_uri()
    return file


def escape(s: str, *, escape_comma: bool = True) -> str:
    """对字符串进行 CQ 码转义。

    参数:
        s: 需要转义的字符串
        escape_comma: 是否转义逗号（`,`）。
    """
    s = s.replace("&", "&amp;").replace("[", "&#91;").replace("]", "&#93;")
    if escape_comma:
        s = s.replace(",", "&#44;")
    return s


def unescape(s: str) -> str:
    """对字符串进行 CQ 码去转义。

    参数:
        s: 需要转义的字符串
    """
    return (
        s.replace("&#44;", ",")
        .replace("&#91;", "[")
        .replace("&#93;", "]")
        .replace("&amp;", "&")
    )

class MessageSegment:
    def __init__(self, type: str, data: Dict[str, Any] = {}):
        self.type = type
        self.data = data or {}

    def __repr__(self):
        return f"MessageSegment(type={self.type}, data={self.data})"

    def __str__(self) -> str:
        if self.is_text():
            return escape(self.data.get("text", ""), escape_comma=False)

        params = ",".join(
            f"{k}={escape(str(v))}" for k, v in self.data.items() if v is not None
        )
        return f"[CQ:{self.type}{',' if params else ''}{params}]"

    def is_text(self) -> bool:
        return self.type == "text"

    @classmethod
    def text(cls, text: str) -> 'MessageSegment':
        return cls("text", {"text": text})

    @classmethod
    def image(
        cls,
        file: Union[str, bytes, BytesIO, Path],
        type_: Optional[str] = None,
        cache: bool = True,
        proxy: bool = True,
        timeout: Optional[int] = None,
    ) -> 'MessageSegment':
        return cls(
            "image",
            {
                "file": f2s(file),
                "type": type_,
                "cache": b2s(cache),
                "proxy": b2s(proxy),
                "timeout": timeout if timeout is None else str(timeout),
            },
        )

    @classmethod
    def anonymous(cls, ignore_failure: Optional[bool] = None) -> Self:
        return cls("anonymous", {"ignore": b2s(ignore_failure)})

    @classmethod
    def at(cls, user_id: Union[int, str]) -> Self:
        return cls("at", {"qq": str(user_id)})

    @classmethod
    def contact(cls, type_: str, id: int) -> Self:
        return cls("contact", {"type": type_, "id": str(id)})

    @classmethod
    def contact_group(cls, group_id: int) -> Self:
        return cls("contact", {"type": "group", "id": str(group_id)})

    @classmethod
    def contact_user(cls, user_id: int) -> Self:
        return cls("contact", {"type": "qq", "id": str(user_id)})

    @classmethod
    def dice(cls) -> Self:
        return cls("dice", {})

    @classmethod
    def face(cls, id_: int) -> Self:
        return cls("face", {"id": str(id_)})

    @classmethod
    def forward(cls, id_: str) -> Self:
        return cls("forward", {"id": id_})

    @classmethod
    def json(cls, data: str) -> Self:
        return cls("json", {"data": data})

    @classmethod
    def location(
        cls,
        latitude: float,
        longitude: float,
        title: Optional[str] = None,
        content: Optional[str] = None,
    ) -> Self:
        return cls(
            "location",
            {
                "lat": str(latitude),
                "lon": str(longitude),
                "title": title,
                "content": content,
            },
        )

    @classmethod
    def music(cls, type_: str, id_: int) -> Self:
        return cls("music", {"type": type_, "id": str(id_)})

    @classmethod
    def music_custom(
        cls,
        url: str,
        audio: str,
        title: str,
        content: Optional[str] = None,
        img_url: Optional[str] = None,
    ) -> Self:
        return cls(
            "music",
            {
                "type": "custom",
                "url": url,
                "audio": audio,
                "title": title,
                "content": content,
                "image": img_url,
            },
        )

    @classmethod
    def node(cls, id_: int) -> Self:
        return cls("node", {"id": str(id_)})

    @classmethod
    def poke(cls, type_: str, id_: str) -> Self:
        return cls("poke", {"type": type_, "id": id_})

    @classmethod
    def record(
        cls,
        file: Union[str, bytes, BytesIO, Path],
        magic: Optional[bool] = None,
        cache: Optional[bool] = None,
        proxy: Optional[bool] = None,
        timeout: Optional[int] = None,
    ) -> Self:
        return cls(
            "record",
            {
                "file": f2s(file),
                "magic": b2s(magic),
                "cache": b2s(cache),
                "proxy": b2s(proxy),
                "timeout": timeout if timeout is None else str(timeout),
            },
        )

    @classmethod
    def reply(cls, id_: int) -> Self:
        return cls("reply", {"id": str(id_)})

    @classmethod
    def rps(cls) -> Self:
        return cls("rps", {})

    @classmethod
    def shake(cls) -> Self:
        return cls("shake", {})

    @classmethod
    def share(
        cls,
        url: str = "",
        title: str = "",
        content: Optional[str] = None,
        image: Optional[str] = None,
    ) -> Self:
        return cls(
            "share", {"url": url, "title": title, "content": content, "image": image}
        )

    @classmethod
    def video(
        cls,
        file: Union[str, bytes, BytesIO, Path],
        cache: Optional[bool] = None,
        proxy: Optional[bool] = None,
        timeout: Optional[int] = None,
    ) -> Self:
        return cls(
            "video",
            {
                "file": f2s(file),
                "cache": b2s(cache),
                "proxy": b2s(proxy),
                "timeout": timeout,
            },
        )

    @classmethod
    def xml(cls, data: str) -> Self:
        return cls("xml", {"data": data})

    @staticmethod
    def _construct(msg: str) -> Iterable['MessageSegment']:
        def _iter_message(msg: str) -> Iterable[Tuple[str, str]]:
            text_begin = 0
            for cqcode in re.finditer(
                r"\[CQ:(?P<type>[a-zA-Z0-9-_.]+)"
                r"(?P<params>"
                r"(?:,[a-zA-Z0-9-_.]+=[^,\]]*)*"
                r"),?\]",
                msg,
            ):
                yield "text", msg[text_begin : cqcode.pos + cqcode.start()]
                text_begin = cqcode.pos + cqcode.end()
                yield cqcode.group("type"), cqcode.group("params").lstrip(",")
            yield "text", msg[text_begin:]

        for type_, data in _iter_message(msg):
            if type_ == "text":
                if data:
                    yield MessageSegment(type_, {"text": unescape(data)})
            else:
                data = {
                    k: unescape(v)
                    for k, v in (
                        x.split("=", maxsplit=1)
                        for x in filter(
                            lambda x: x, (x.lstrip() for x in data.split(","))
                        )
                    )
                }
                yield MessageSegment(type_, data)