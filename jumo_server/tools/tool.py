from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from anthropic.types.tool_param import ToolParam 

InputType = TypeVar("InputType")
OutputType = TypeVar("OutputType")

class Tool(Generic[InputType, OutputType], ABC):
    name: str
    description: str

    @abstractmethod
    def json(self) -> ToolParam:
        pass

    @abstractmethod
    async def impl(self, input: InputType) -> OutputType:
        pass
