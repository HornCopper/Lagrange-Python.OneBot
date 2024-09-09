from typing import Literal

from .ManualEvent import Event

class RequestEvent(Event):
    post_type: str = "request"

class FriendRequestEvent(RequestEvent):
    request_type: str = "friend"
    user_id: int = 0
    comment: str = ""
    flag: str = ""

class GroupRequestEvent(RequestEvent):
    request_type: str = "group"
    sub_type: Literal["add", "invite"] = "add"
    group_id: int = 0
    user_id: int = 0
    comment: str = ""
    flag: str = ""