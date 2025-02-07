from anthropic.types.tool_param import ToolParam
from typing_extensions import TypedDict

from jumo_server.tools.tool import Tool


class ExtractGraphKnowledgeItem(TypedDict):
    id: str
    type: str


class ExtractGraphKnowledgeRelationshipItem(TypedDict):
    head: str
    tail: str
    type: str
    inverse: str


class ExtractGraphKnowledgeOutput(TypedDict):
    entities: list[ExtractGraphKnowledgeItem]
    relationships: list[ExtractGraphKnowledgeRelationshipItem]


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
                "required": ["entities", "relationships"],
                "additionalProperties": False,
                "properties": {
                    "entities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["id", "type"],
                            "properties": {
                                "id": {"type": "string"},
                                "type": {
                                    "type": "string",
                                },
                            },
                        },
                    },
                    "relationships": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["head", "type", "tail", "inverse"],
                            "properties": {
                                "head": {"type": "string"},
                                "tail": {"type": "string"},
                                "type": {"type": "string"},
                                "inverse": {"type": "string"},
                            },
                        },
                    },
                },
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
