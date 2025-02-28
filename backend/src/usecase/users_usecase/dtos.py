from pydantic import BaseModel
from typing import List


class ResponseUsers(BaseModel):
    users: List[str]