from typing_extensions import TypedDict
from anthropic.types.tool_param import ToolParam
from jumo_server.db.graph_db import graph_db
from jumo_server.llm.llm import make_llm_tool_call
from jumo_server.tools.tool import Tool


class ExtractMemoryRelation(TypedDict):
    source: str
    target: str
    type: str


class ExtractMemoryOutput(TypedDict):
    entities: list[str]
    relations: list[ExtractMemoryRelation]


# Much of this taken from https://github.com/langchain-ai/langchain-experimental/blob/main/libs/experimental/langchain_experimental/graph_transformers/llm.py

examples = [
    {
        "text": (
            "Adam is a software engineer in Microsoft since 2009, "
            "and last year he got an award as the Best Talent"
        ),
        "head": "Adam",
        "head_type": "Person",
        "relation": "WORKS_FOR",
        "tail": "Microsoft",
        "tail_type": "Company",
    },
    {
        "text": (
            "Adam is a software engineer in Microsoft since 2009, "
            "and last year he got an award as the Best Talent"
        ),
        "head": "Adam",
        "head_type": "Person",
        "relation": "HAS_AWARD",
        "tail": "Best Talent",
        "tail_type": "Award",
    },
    {
        "text": (
            "Microsoft is a tech company that provide "
            "several products such as Microsoft Word"
        ),
        "head": "Microsoft Word",
        "head_type": "Product",
        "relation": "PRODUCED_BY",
        "tail": "Microsoft",
        "tail_type": "Company",
    },
    {
        "text": "Microsoft Word is a lightweight app that accessible offline",
        "head": "Microsoft Word",
        "head_type": "Product",
        "relation": "HAS_CHARACTERISTIC",
        "tail": "lightweight app",
        "tail_type": "Characteristic",
    },
    {
        "text": "Microsoft Word is a lightweight app that accessible offline",
        "head": "Microsoft Word",
        "head_type": "Product",
        "relation": "HAS_CHARACTERISTIC",
        "tail": "accessible offline",
        "tail_type": "Characteristic",
    },
]

system_prompt = (
    "# Knowledge Graph Instructions for GPT-4\n"
    "## 1. Overview\n"
    "You are a top-tier algorithm designed for extracting information in structured "
    "formats to build a knowledge graph.\n"
    "Try to capture as much information from the text as possible without "
    "sacrificing accuracy. Do not add any information that is not explicitly "
    "mentioned in the text.\n"
    "- **Nodes** represent entities and concepts.\n"
    "- The aim is to achieve simplicity and clarity in the knowledge graph, making it\n"
    "accessible for a vast audience.\n"
    "## 2. Labeling Nodes\n"
    "- **Consistency**: Ensure you use available types for node labels.\n"
    "Ensure you use basic or elementary types for node labels.\n"
    "- For example, when you identify an entity representing a person, "
    "always label it as **'person'**. Avoid using more specific terms "
    "like 'mathematician' or 'scientist'."
    "- **Node IDs**: Never utilize integers as node IDs. Node IDs should be "
    "names or human-readable identifiers found in the text.\n"
    "- **Relationships** represent connections between entities or concepts.\n"
    "Ensure consistency and generality in relationship types when constructing "
    "knowledge graphs. Instead of using specific and momentary types "
    "such as 'BECAME_PROFESSOR', use more general and timeless relationship types "
    "like 'PROFESSOR'. Make sure to use general and timeless relationship types!\n"
    "## 3. Coreference Resolution\n"
    "- **Maintain Entity Consistency**: When extracting entities, it's vital to "
    "ensure consistency.\n"
    'If an entity, such as "John Doe", is mentioned multiple times in the text '
    'but is referred to by different names or pronouns (e.g., "Joe", "he"),'
    "always use the most complete identifier for that entity throughout the "
    'knowledge graph. In this example, use "John Doe" as the entity ID.\n'
    "Remember, the knowledge graph should be coherent and easily understandable, "
    "so maintaining consistency in entity references is crucial.\n"
    "## 4. Strict Compliance\n"
    "Adhere to the rules strictly. Non-compliance will result in termination."
)


class ExtractEntitiesTool(Tool[ExtractMemoryOutput, ExtractMemoryOutput]):
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
                            "type": "string",
                        },
                    },
                    "relations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "source": {
                                    "type": "string",
                                },
                                "target": {
                                    "type": "string",
                                },
                                "type": {
                                    "type": "string",
                                },
                            },
                        },
                    },
                },
                "required": ["entities"],
            },
        }

    async def impl(self, input: ExtractMemoryOutput) -> ExtractMemoryOutput:
        return input


class GraphMemory:
    async def extract_entities(self, input: str):
        result = await make_llm_tool_call(
            query=input, tool=ExtractEntitiesTool(), system=EXTRACT_ENTITIES_PROMPT
        )

        if result:
            async with graph_db.session() as session:
                for entity in result["entities"]:
                    await session.run("MERGE (e:Entity {name: $name})", name=entity)

                for relation in result["relations"]:
                    await session.run(
                        """
                        MATCH (source:Entity {name: $source})
                        MATCH (target:Entity {name: $target})
                        CREATE (source)-[:RELATION {type: $type}]->(target)
                        """,
                        source=relation["source"],
                        target=relation["target"],
                        type=relation["type"],
                    )

        return result


EXTRACT_ENTITIES_PROMPT = """You are an expert entity extraction system.
Your task is to identify and extract entities from provided text, along with their relationships and attributes.

The person who is making the message is Ryan.
"""


# Follow these guidelines:
#
# PERSON: Individual human beings
# ORGANIZATION: Companies, institutions, agencies, etc.
# LOCATION: Physical locations, cities, countries, etc.
# DATE: Temporal expressions and dates
# PRODUCT: Products, services, or works
# EVENT: Named events or incidents
# QUANTITY: Measurable quantities with units
# TECHNOLOGY: Technical systems, methods, or tools
# CONCEPT: Abstract ideas or theoretical constructs
#
# RELATIONSHIP TYPES:
#
# WORKS_FOR: Employment or organizational membership
# LOCATED_IN: Physical or geographical containment
# PART_OF: Component or membership relationship
# CREATED_BY: Authorship or creation relationship
# INTERACTS_WITH: General interaction or connection
# LEADS: Leadership or management relationship
# OWNS: Ownership or possession
# USES: Usage or utilization relationship
#
# SPECIAL INSTRUCTIONS:
#
# For ambiguous entities, include all possible interpretations with appropriate confidence scores
# Link abbreviated mentions to their full forms
# Include relevant metadata and qualifiers as attributes
# Identify nested or overlapping entities
# Preserve case sensitivity where meaningful
# Extract role and title information as attributes
# Note temporal qualifiers for relationships
# Include modality and certainty attributes for relationships
#
# Remember:
#
# Always output valid JSON
# Include position information for all mentions
# Assign confidence scores for uncertain extractions
# Link related mentions of the same entity
# Extract both explicit and implicit relationships
# Preserve contextual information in attributes


# GUIDELINES:
#
# Extract both explicit and implicit relationships between entities
# Normalize entity names while preserving original mentions
# Identify and link co-referential mentions of the same entity
# Extract temporal and contextual attributes when relevant
