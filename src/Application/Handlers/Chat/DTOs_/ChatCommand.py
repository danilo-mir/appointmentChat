from uuid import UUID
from typing import List

from pydantic import BaseModel


class ChatCommand(BaseModel):
    session_id: UUID
    context: List[str]
