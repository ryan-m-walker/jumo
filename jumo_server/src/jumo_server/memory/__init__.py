from mem0 import Memory


config = {
    "version": "v1.1",
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
        },
    },
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
