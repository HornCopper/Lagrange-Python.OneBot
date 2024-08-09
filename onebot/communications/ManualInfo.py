from pydantic import BaseModel

class GroupInfo(BaseModel):
    group_id: int = 0
    group_name: str = ""
    member_count: int = 0
    max_member_count: int = 0