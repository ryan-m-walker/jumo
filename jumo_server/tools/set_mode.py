from typing import Literal, TypedDict
from anthropic.types.tool_param import ToolParam
from jumo_server.events import event_manager

from jumo_server.tools.tool import Tool

class SetModeToolInput(TypedDict):
    mode: Literal["default", "debug"]

class SetModeToolOutput(TypedDict):
    new_mode: Literal["default", "debug"]

class SetModeTool(Tool[SetModeToolInput, SetModeToolOutput]):
    name = "set_mode"
    description = """Toggle which interface mode you will be displaying on your display screen"""

    async def impl(self, input: SetModeToolInput) -> SetModeToolOutput:
        await event_manager.broadcast_to_all({"type": "ModeChange", "mode": input['mode']})
        return { "new_mode": input['mode'] }


    def json(self) -> ToolParam:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["default", "debug"],
                    },
                },
                "required": ["mode"],
            }
        }
