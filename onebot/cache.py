from datetime import datetime
from typing import Optional

import random

uid_uin_dict = {}
msg_id_dict = {}
group_requests = {}

def get_uid_by_uin(uin: int) -> Optional[str]:
    return uid_uin_dict.get(uin)

def get_uin_by_uid(uid: str) -> Optional[int]:
    for uin in uid_uin_dict:
        if uid_uin_dict[uin] == uid:
            return uin

def get_rdnum(repeat: list, retry: int):
    if retry > 50000000:
        raise MemoryError("Message Id is actually not enough, please restart the application.")
    msg_id = str(random.randint(-2147483647, 2147483647))
    if msg_id in repeat:
        return get_rdnum(repeat, retry+1)
    else:
        return msg_id

def save_msg(seq: int, group_id: int) -> int:
    msg_id: str = get_rdnum(list(msg_id_dict), 0)
    msg_id_dict[msg_id] = {"seq": seq, "time": int(datetime.now().timestamp()), "group_id": group_id}
    return int(msg_id)

def get_seq(msg_id: int):
    for i in msg_id_dict:
        if i == msg_id:
            seq = msg_id_dict[i]["seq"]
            group_id = msg_id_dict[i]["group_id"]
            return seq, group_id
        