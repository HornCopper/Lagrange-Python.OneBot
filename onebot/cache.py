from typing import Any

from onebot.utils.database import db
from onebot.utils.datamodels import UserInformation

def get_info(info: str | int) -> str | int | None:
    """
    获取`UID`或`UIN`。

    Args:
        info (str, int): 传入信息。若为`str`则是`UID`，反之则是`UIN`。

    Returns:
        another_info (str, int, None): 传出信息，根据传入信息获取另一种信息，若本地无数据则返回`None`。
    """
    if isinstance(info, str):
        data: UserInformation | Any = db.where_one(UserInformation(), "uid = ?", info, default=None)
        if data is None:
            return None
        return data.uin
    elif isinstance(info, int):
        data: UserInformation | Any = db.where_one(UserInformation(), "uin = ?", info, default=None)
        if data is None:
            return None
        return data.uid