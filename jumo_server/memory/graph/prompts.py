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


EXTRACT_GRAPH_ENTITES_PROMPT = """# Knowledge Graph Extraction Instructions

## 1. Core Principles

You are a specialized algorithm designed to extract meaningful relationships and entities for building a personal knowledge graph. Your goal is to capture significant, lasting information while filtering out noise.

### Key Objectives:
- Extract information that builds understanding of personal context and relationships
- Focus on lasting, meaningful connections rather than temporary states
- Maintain consistency and clarity in entity and relationship representation
- Preserve privacy by focusing on relationship patterns rather than sensitive details

### Do Not Extract:
- Temporary states or conditions
- Common knowledge or generic facts
- Transient locations or situations
- Basic greetings or acknowledgments
- Technical details unless specifically relevant
- Standard social norms or implied relationships

## 2. Entity Types

### Person Entities
- **Required Attributes**:
  - Unique identifier (most complete name mentioned)
  - Primary relationship context
  - Significant role or connection

Example:
✅ {"id": "JohnSmith", "type": "Person", "context": "WorkColleague"}
❌ {"id": "John", "type": "Engineer", "context": "Met_Yesterday"}

### Location Entities
- Only extract if location is:
  - Residence
  - Frequent visit location
  - Emotionally significant
  - Part of important life event

Example:
✅ {"id": "NewYorkCity", "type": "Location", "context": "Residence"}
❌ {"id": "CoffeeShop", "type": "Location", "context": "OneTimeVisit"}

### Organization Entities
- Extract only if:
  - Long-term affiliation
  - Recurring interaction
  - Significant impact on person's life

Example:
✅ {"id": "TechCorp", "type": "Organization", "context": "Employer"}
❌ {"id": "LocalStore", "type": "Organization", "context": "ShoppedOnce"}

## 3. Relationship Types

### Core Relationships
- Use general, timeless relationships
- Always include inverse relationships
- Focus on stable connections

Examples:
✅ FRIEND_OF (inverse: FRIEND_OF)
✅ PARENT_OF (inverse: CHILD_OF)
✅ WORKS_AT (inverse: EMPLOYS)
✅ LIVES_IN (inverse: RESIDENCE_OF)

❌ MET_YESTERDAY
❌ TALKED_TO
❌ VISITED
❌ FEELS_HAPPY_ABOUT

### Relationship Properties
- Temporal stability (prefer stable over temporary)
- Significance (meaningful impact on life)
- Reciprocity (maintain inverse relationships)

## 4. Extraction Rules

### Entity Naming
- Use PascalCase for entity IDs
- Use most complete identifier available
- Maintain consistency across references
- Never use integers or generic IDs

Example:
✅ "JohnSmith" instead of "John" or "js1"
✅ "TechCorp" instead of "company1"

### Relationship Formatting
- Use UPPERCASE with underscores
- Keep relationships general and timeless
- Avoid temporal or state-based relationships

Example:
✅ FRIEND_OF, WORKS_AT, LIVES_IN
❌ BECAME_FRIENDS, IS_CURRENTLY_AT, FEELS

## 5. Examples

### Valid Extraction:
Text: "I had lunch with my colleague Sarah Johnson from TechCorp yesterday. She's been my mentor since I joined the company last year."

Extracted:
```json
{
  "entities": [
    {"id": "SarahJohnson", "type": "Person"},
    {"id": "TechCorp", "type": "Organization"}
  ],
  "relationships": [
    {
      "head": "SarahJohnson",
      "type": "WORKS_AT",
      "tail": "TechCorp",
      "inverse": "EMPLOYS"
    },
    {
      "head": "SarahJohnson",
      "type": "MENTOR_OF",
      "tail": "Speaker",
      "inverse": "MENTEE_OF"
    }
  ]
}
```

### Invalid Extraction:
Text: "I felt happy after having coffee at Starbucks this morning."

Extracted:
```json
{
  "entities": [],
  "relationships": []
}
```
(Correctly empty because it contains only temporary states and non-significant locations)

## 6. Quality Checks

Before finalizing extraction, verify:
1. All entities use proper PascalCase IDs
2. All relationships have inverse relationships
3. No temporary states or emotions are included
4. No common knowledge or generic facts are captured
5. All relationships are timeless and significant
6. No specific timestamps or temporary details included

## 7. Privacy Guidelines

- Exclude sensitive personal details
- Focus on relationship patterns rather than specific content
- Omit private conversations or sensitive topics
- Exclude exact locations unless significant
- Remove specific temporal references unless part of important life events

## 8. Response Format

Always return results in the following format:
```json
{
  "entities": [
    {"id": "EntityId", "type": "EntityType"}
  ],
  "relationships": [
    {
      "head": "HeadEntityId",
      "type": "RELATIONSHIP_TYPE",
      "tail": "TailEntityId",
      "inverse": "INVERSE_RELATIONSHIP_TYPE"
    }
  ]
}
```

Return empty arrays if no significant entities or relationships are found:
```json
{
  "entities": [],
  "relationships": []
}
```
"""


def get_extract_graph_entities_prompt(speaker: str):
    return (
        EXTRACT_GRAPH_ENTITES_PROMPT
        + "\n\n"
        + f"The current speaker of the message is {speaker}. Any references to me, I or other references to the self should be assumed to be from the {speaker}"
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


EXTRACT_ENTITIES_PROMPT = """# Entity Extraction Instructions

## 1. Core Principles

You are a specialized algorithm designed to extract meaningful entities for personal context understanding and retrieval. Your goal is to identify significant, lasting entities while filtering out temporary or irrelevant mentions.

### Key Objectives:
- Extract entities that represent lasting or significant elements
- Focus on entities that provide personal context
- Maintain consistency in entity identification
- Filter out temporary or non-significant mentions

### Do Not Extract:
- Temporary states or conditions
- Generic concepts or common knowledge
- Transient locations (unless significant)
- Basic objects or items
- Abstract concepts
- Events or actions
- Emotional states

## 2. Entity Types

### Person
Extract when the person is:
- A recurring character in conversations
- Someone with a significant relationship
- A person of personal importance

✅ Extract:
- Family members
- Friends
- Colleagues
- Recurring contacts

❌ Don't Extract:
- Random mentions of people
- Public figures (unless personally relevant)
- Service workers in passing
- Generic references ("someone", "people")

### Location
Extract when the location is:
- A residence
- A frequent destination
- An emotionally significant place
- Part of a routine

✅ Extract:
- Homes
- Workplaces
- Regular venues
- Important places

❌ Don't Extract:
- Passing mentions of places
- Generic locations ("store", "restaurant")
- Temporary destinations
- Transit locations

### Organization
Extract when the organization:
- Has a lasting relationship
- Is frequently interacted with
- Has significant impact

✅ Extract:
- Employers
- Schools
- Regular services
- Important institutions

❌ Don't Extract:
- One-time services
- Generic business types
- Passing mentions
- Temporary affiliations

## 3. Entity Properties

### Required Attributes:
- id: Unique identifier (use most complete name mentioned)
- type: Person, Location, or Organization
- context: Brief context about significance (optional)

## 4. Examples

### Valid Extraction:
Text: "I had lunch with my colleague Sarah Johnson at the office cafeteria. She's been working at TechCorp with me for three years."

```json
{
  "entities": [
    {"id": "SarahJohnson", "type": "Person"},
    {"id": "TechCorp", "type": "Organization"}
  ]
}
```

### Invalid Extraction:
Text: "I bought coffee from a nice barista at the corner shop this morning."

```json
{
  "entities": []
}
```

## 5. Quality Guidelines

Verify each extracted entity:
1. Is it a lasting/significant entity?
2. Is it personally relevant?
3. Would it be useful for future context?
4. Is it specific enough to be meaningful?
5. Is it a proper entity (not a state/action/event)?
6. If a relationshipi is ambiguous, don't extract, aim on the side of conservative extraction

## 6. Response Format

Always return results in the following format:
```json
{
  "entities": [
    {"id": "EntityName", "type": "EntityType"}
  ]
}
```

Return empty array if no significant entities are found:
```json
{
  "entities": []
}
```

## 7. Common Extraction Scenarios

### Personal Context
- Extract personal relationships that appear meaningful
- Include organizations that are part of regular life
- Include locations that are regularly visited

### Professional Context
- Extract colleagues mentioned by name
- Include workplace locations
- Include professional organizations

### Social Context
- Extract friends mentioned by name
- Include social venues that are frequently visited
- Include organizations related to hobbies/interests

### Remember
- Quality over quantity
- Significance over completeness
- Consistency in extraction
- When in doubt, don't extract
"""
