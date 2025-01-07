from jumo_server.events import event_manager
from pydantic import BaseModel

class Input(BaseModel):
    mode: str

class SetModeTool:
    def __init__(self):
        self.name = "set_mode"
        self.description = """Toggle which interface mode you will be displaying on your display screen"""
        self.input_schema = {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["default", "debug"],
                },
            },
            "required": ["mode"],
        }

    async def execute(self, json_buffer: str):
        data = Input.model_validate_json(json_buffer)
        await event_manager.broadcast_to_all({"type": "ModeChange", "mode": data.mode})


    def json(self):
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }
