from mem0 import Memory

from jumo_server.prompts import MEMORY_EXTRACTION_PROMPT


config = {
    "version": "v1.1",
    "llm": {
        "provider": "anthropic",
        "config": {
            "model": "claude-3-5-sonnet-latest",
        },
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
        },
    },
    "custom_prompt": MEMORY_EXTRACTION_PROMPT,
    # "graph_store": {
    #     "provider": "neo4j",
    #     "config": {
    #         "url": "neo4j://localhost:7687",
    #         "username": "neo4j",
    #         "password": "secretgraph",
    #     },
    # },
}

memory = None


def memory_client():
    global memory

    if memory is None:
        memory = Memory.from_config(config)

    return memory
