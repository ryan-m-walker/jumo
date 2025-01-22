from jumo_server.db.graph_db import graph_db
from jumo_server.embeddings import Embedder
from jumo_server.llm.llm import make_llm_tool_call
from jumo_server.memory.graph.prompts import (
    EXTRACT_ENTITIES_PROMPT,
    EXTRACT_GRAPH_ENTITES_PROMPT,
)
from jumo_server.memory.graph.tools import (
    ExtractEntitiesTool,
    ExtractGraphKnowledgeTool,
)


class GraphMemory:
    embedder = Embedder()

    async def search(self, entity_type: str, entity_id: str, limit: int = 10):
        search_embedding = await self.embedder.embed(
            entity_type + ":" + entity_id, dimensions=256
        )

        async with graph_db.session() as session:
            res = await session.run(
                """
                MATCH (node:Entity)
                WITH node, vector.similarity.cosine(node.embedding, $embedding) AS score
                WHERE score > 0.9
                RETURN node, score
                ORDER BY score DESC LIMIT 10;
                """,
                embedding=search_embedding,
            )

            print(res)

            return await res.data()

    async def extract_relationships(self, input: str):
        result = await make_llm_tool_call(
            query=input,
            tool=ExtractGraphKnowledgeTool(),
            system=EXTRACT_GRAPH_ENTITES_PROMPT,
        )

        if result:
            async with graph_db.session() as session:
                for entity in result["entities"]:
                    head_embedding = await self.embedder.embed(
                        entity["head_type"] + ":" + entity["head"],
                        dimensions=256,
                    )

                    await session.run(
                        """
                        CALL apoc.merge.node($labels, $props) YIELD node
                        SET node.embedding = $embedding
                        RETURN node
                        """,
                        labels=["Entity", entity["head_type"]],
                        props={"id": entity["head"], "type": entity["head_type"]},
                        embedding=head_embedding,
                    )

                    tail_embedding = await self.embedder.embed(
                        entity["tail_type"] + ":" + entity["tail"],
                        dimensions=256,
                    )

                    await session.run(
                        """
                        CALL apoc.merge.node($labels, $props) YIELD node
                        SET node.embedding = $embedding
                        RETURN node
                        """,
                        labels=["Entity", entity["tail_type"]],
                        props={"id": entity["tail"], "type": entity["tail_type"]},
                        embedding=tail_embedding,
                    )

                    await session.run(
                        """
                        MATCH (head:Entity {id: $head_id})
                        MATCH (tail:Entity {id: $tail_id})
                        CALL apoc.create.relationship(head, $relation, {}, tail)
                        YIELD rel
                        RETURN rel
                        """,
                        head_id=entity["head"],
                        tail_id=entity["tail"],
                        relation=entity["relation"],
                    )

        return result

    # async def search(self, input: str):
    #     result = await self.extract_entities(input)
    #
    #     if not result or len(result["entities"]) == 0:
    #         return None
    #
    #     for entity in result["entities"]:
    #         embedding = await self.embedder.embed(entity["type"] + ":" + entity["name"])

    async def extract_entities(self, input: str):
        return await make_llm_tool_call(
            query=input,
            tool=ExtractEntitiesTool(),
            system=EXTRACT_ENTITIES_PROMPT,
            model="claude-3-5-haiku-latest",
        )
