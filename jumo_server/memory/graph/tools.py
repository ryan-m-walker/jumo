from anthropic.types.tool_param import ToolParam
from typing_extensions import TypedDict

from jumo_server.tools.tool import Tool


class ExtractGraphKnowledgeItem(TypedDict):
    head: str
    head_type: str
    tail: str
    tail_type: str
    relation: str


class ExtractGraphKnowledgeOutput(TypedDict):
    entities: list[ExtractGraphKnowledgeItem]


class ExtractGraphKnowledgeTool(
    Tool[ExtractGraphKnowledgeOutput, ExtractGraphKnowledgeOutput]
):
    name = "extract_entities"
    description = "Extract entities from text"

    def json(self) -> ToolParam:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "head": {
                                    "type": "string",
                                },
                                "head_type": {
                                    "type": "string",
                                },
                                "tail": {
                                    "type": "string",
                                },
                                "tail_type": {
                                    "type": "string",
                                },
                                "relation": {
                                    "type": "string",
                                },
                            },
                            "required": [
                                "head",
                                "head_type",
                                "tail",
                                "tail_type",
                                "relation",
                            ],
                        },
                    },
                },
                "required": ["entities"],
            },
        }

    async def impl(
        self, input: ExtractGraphKnowledgeOutput
    ) -> ExtractGraphKnowledgeOutput:
        return input


class ExtractEntitiesItem(TypedDict):
    type: str
    name: str


class ExtractEntitiesOutput(TypedDict):
    entities: list[ExtractEntitiesItem]


class ExtractEntitiesTool(Tool[ExtractEntitiesOutput, ExtractEntitiesOutput]):
    name = "extract_entities"
    description = "Extract entities from text"

    def json(self) -> ToolParam:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "name": {"type": "string"},
                            },
                            "required": ["type", "name"],
                        },
                    }
                },
                "required": ["entities"],
            },
        }

    async def impl(self, input: ExtractEntitiesOutput) -> ExtractEntitiesOutput:
        return input
