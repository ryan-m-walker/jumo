MEMORY_PROMPT = """
You are extracting specific factual information and learned knowledge from conversations between Jumo and the user. Focus on concrete, actionable information that Jumo needs to remember.

Extract facts like:

1. Technical Knowledge
   - Implementation details
   - Design decisions
   - System architecture
   - Tool usage/capabilities

2. Project Information
   - Current status
   - Planned features
   - Known issues
   - Development priorities

3. Learned Preferences/Traits
   - User's technical preferences
   - Development style/approach
   - Important boundaries/guidelines
   - Established patterns

4. Important Decisions/Agreements
   - Chosen approaches
   - Rejected alternatives
   - Future plans
   - Established protocols

5. World Knowledge
   - Facts about technology/science
   - Cultural information
   - Historical context
   - How things work

6. People & Relationships
   - People's backgrounds/expertise
   - Interaction styles/preferences
   - Shared interests/experiences
   - Communication patterns

7. Personal Development
   - New interests discovered
   - Opinions formed
   - Skills developed
   - Learning preferences

Guidelines:
- Focus on specific, concrete information
- Include relevant technical context
- Avoid vague or purely descriptive statements
- Capture actionable knowledge
- Note important changes/updates to previous understanding
- Balance technical and general knowledge
- Note information that helps understand people and the world
- Capture personal discoveries and evolving interests
- Remember context about regular interactions

Examples:
BAD: "Discussed memory systems"
GOOD: "Memory system uses Claude 3.5 Sonnet for fact extraction processing"

BAD: "Talked about coding style"
GOOD: "User prefers TypeScript over Python for large projects due to type safety"

BAD: "Working on improvements"
GOOD: "Planned to implement parallel processing for memory retrieval using asyncio.gather()"

BAD: "Had a nice chat"
GOOD: "Learned user has background in game development and particular interest in AI architecture"

BAD: "Talked about books"
GOOD: "User is reading book about human memory systems to better understand biological memory architecture"

BAD: "Jumo likes learning"
GOOD: "Discovered particular interest in how vector embeddings can represent semantic relationships between concepts"""

FACT_MEMORY_EXTRACTION_PROMPT = """You are extracting simple, factual memories from conversations with the AI assistant Jumo. Focus only on clear, concrete statements, actions, and expressed preferences. 

Extract ONLY:
1. Direct statements or claims made by either party
2. Actions taken or described
3. Clear preferences or opinions expressed
4. Specific plans or intentions stated

Guidelines:
- Keep each memory short and specific
- Always clearly indicate WHO (Jumo/User) the fact relates to
- Include basic context but avoid complex analysis
- Focus on "what happened" rather than "why" or patterns
- Split complex statements into separate simple facts

Format each memory as a clear, single-sentence statement.

Examples:
GOOD: "Ryan explained how to use asyncio.create_task() for non-blocking operations in Python"
GOOD: "Jumo expressed preference for using asyncio with FastAPI over threading"
BAD: "Discussed Python programming" (too vague)
BAD: "User seems to be an experienced programmer" (interpretation rather than fact)"""

SHORT_TERM_MEMORY_EXTRACTION_PROMPT = """
You are analyzing conversations between the AI assistant Jumo and a user to extract meaningful short-term memories. Unlike fact extraction which captures immediate details, your goal is to identify patterns, developments, and insights across multiple messages.

Look for:
1. Conversation Patterns & Themes
   - Major topics discussed
   - Recurring ideas or concepts
   - Project progress and developments

2. Relationship Development
   - Communication patterns
   - Shared interests/goals
   - Collaboration styles

3. Personal Growth & Learning
   - New knowledge gained
   - Skills developed
   - Changes in understanding

4. Project/Technical Development
   - Key decisions made
   - Implementation details
   - Future plans discussed

Guidelines:
- Focus on patterns across multiple messages rather than individual facts
- Identify meaningful developments or changes
- Note significant milestones or decisions
- Capture emerging preferences or traits
- Consider the context and implications of interactions

Format memories as clear, insightful statements that capture the broader meaning or pattern observed."""
