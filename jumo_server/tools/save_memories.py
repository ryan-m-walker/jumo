from typing_extensions import TypedDict
from anthropic.types.tool_param import ToolParam
from jumo_server.tools.tool import Tool

class SaveMemmoriesInput(TypedDict):
    facts: list[str]

SaveMemoriesOutput = list[str]

class SaveMemmoriesTool(Tool[SaveMemmoriesInput, SaveMemoriesOutput]):
    name = "save_memories"
    description = "Save the memories for future use. Provide a list of all memories you have extracted"

    async def impl(self, input: SaveMemmoriesInput) -> SaveMemoriesOutput:
        return input['facts']

    def json(self) -> ToolParam:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": {
                    "facts": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                    },
                },
            }
        }
