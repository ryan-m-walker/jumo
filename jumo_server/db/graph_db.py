from neo4j import AsyncGraphDatabase


URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "secretgraph")


graph_db = AsyncGraphDatabase.driver(URI, auth=AUTH)


async def init_graph_db():
    async with graph_db.session() as session:
        await session.run(
            """
            CREATE VECTOR INDEX `embeddings` IF NOT EXISTS
            FOR (n:Entity) ON (n.embedding)
            OPTIONS {
                indexConfig: {
                    `vector.dimensions`: 256,
                    `vector.similarity_function`: 'cosine'
                }
            }
            """
        )
