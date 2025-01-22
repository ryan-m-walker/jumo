# Much of this taken from https://github.com/langchain-ai/langchain-experimental/blob/main/libs/experimental/langchain_experimental/graph_transformers/llm.py

EXTRACT_GRAPH_ENTITIES_EXAMPLES = [
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


def format_examples(examples):
    return "\n".join(
        [
            f"### Example {i + 1}\n"
            f"**Text**: {example['text']}\n"
            f'**Output**: {{ "head": "{example["head"]}", "head_type": "{example["head_type"]}", "relation": "{example["relation"]}", "tail": "{example["tail"]}", "tail_type": "{example["tail_type"]}" }}'
            for i, example in enumerate(examples)
        ]
    )


EXTRACT_GRAPH_ENTITES_PROMPT = (
    "# Knowledge Graph Instructions\n"
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
    "- Node IDs (head and tail) and types (head_type and tail_type) should be Pascal case"
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
    "Adhere to the rules strictly. Non-compliance will result in termination.\n"
    "The current speaker of the message is Ryan\n"
    '## 5. Make sure to include inverted relationships. For example, if the text says "A is B\'s pet", then the relationship should be "PET" and the inverse relationship should be "OWNER"\n'
    "## Examples\n"
    f"{format_examples(EXTRACT_GRAPH_ENTITIES_EXAMPLES)}\n"
)

EXTRACT_ENTITIES_EXAMPLES = [
    {
        "text": (
            "Adam is a software engineer in Microsoft since 2009, "
            "and last year he got an award as the Best Talent"
        ),
        "entities": [
            {"name": "Adam", "type": "Person"},
            {"name": "Microsoft", "type": "Company"},
            {"name": "BestTalent", "type": "Award"},
        ],
    },
    {
        "text": (
            "Microsoft is a tech company that provide "
            "several products such as Microsoft Word"
        ),
        "entities": [
            {"name": "Microsoft", "type": "Company"},
            {"name": "MicrosoftWord", "type": "Product"},
        ],
    },
]


def format_entities(examples):
    return "\n".join(
        [
            f"### Example {i + 1}\n"
            f"**Text**: {example['text']}\n"
            f"**Output**: {example['entities']}"
            for i, example in enumerate(examples)
        ]
    )


EXTRACT_ENTITIES_PROMPT = (
    "# Entity Extraction Instructions\n"
    "## 1. Overview\n"
    "You are a top-tier algorithm designed for extracting entities from text.\n"
    "The aim is to capture as much information from the text as possible without "
    "sacrificing accuracy. Do not add any information that is not explicitly "
    "mentioned in the text.\n"
    "Entities can be any noun or noun phrase in the text.\n"
    "Format the name of the entity in Pascal case.\n"
    "You should capture the id or name of the entity and its type.\n"
    "## Examples\n"
    f"{format_entities(EXTRACT_ENTITIES_EXAMPLES)}\n"
)
