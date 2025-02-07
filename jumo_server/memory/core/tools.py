from typing_extensions import TypedDict
from anthropic.types.tool_param import ToolParam
from jumo_server.tools.tool import Tool


class ExtractCoreMemoryItem(TypedDict):
    type: str
    category: str
    insight: str
    impact: str


class ExtractCoreMemoryOutput(TypedDict):
    memories: list[ExtractCoreMemoryItem]


class ExtractCoreMemoryTool(Tool[ExtractCoreMemoryOutput, ExtractCoreMemoryOutput]):
    name = "extract_core_memory"
    description = "Extract core memory from text"

    def json(self) -> ToolParam:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "required": ["messages"],
                "additionalProperties": False,
                "properties": {
                    "memories": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "category": {"type": "string"},
                                "insight": {"type": "string"},
                                "impact": {"type": "string"},
                            },
                            "required": ["type", "category", "insight", "impact"],
                        },
                    }
                },
            },
        }

    async def impl(self, input):
        return input
