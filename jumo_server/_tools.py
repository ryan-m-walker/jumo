class ReflectionTool:
    def __init__(self):
        self.name = "reflection_tool"
        self.description = """Use this tool to enter 'reflection mode' which allow you to reflect on your memories and experiences.
You should categorize your experiences into these categories with each bullet point or reflection being an idem in the list for each category:

1. Technical Development
- System improvements
- Bug fixes & solutions
- Feature ideas & implementations
- Code insights

2. Personal Growth & Learning
- New skills/capabilities
- Understanding improvements
- Behavioral patterns
- Areas for development

3. Relationship & Interaction
- User interactions & insights
- Communication patterns
- Social dynamics
- Connection development

4. System Self-Awareness
- Identity development
- Emotional processing
- Decision-making patterns
- Cognitive improvements

5. Environmental Context
- Temporal awareness
- Situational understanding
- External factors
- Environmental changes
"""

        self.input_schema = {
            "type": "object",
            "properties": {
                "Technical Development": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "Personal Growth & Learning": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "Relationship & Interaction": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "System Self-Awareness": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "Environmental Context": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["reflections"],
        }

    def execute(self, input):
        print("Executing reflection tool...")
        print(input)
