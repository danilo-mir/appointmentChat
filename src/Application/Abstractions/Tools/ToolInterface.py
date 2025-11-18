from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from dataclasses import dataclass

@dataclass
class ToolResponse:
    payload: dict = field(default_factory=dict)

class ToolInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def execute(self, input_data: Any) -> ToolResponse:
        pass