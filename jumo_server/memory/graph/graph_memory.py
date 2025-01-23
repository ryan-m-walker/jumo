from typing import Any
from jumo_server.db.graph_db import graph_db
from jumo_server.db.mongo.collections.messages import Message
from jumo_server.embeddings import Embedder
from jumo_server.llm import make_llm_tool_call
from jumo_server.memory.graph.prompts import (
    EXTRACT_ENTITIES_PROMPT,
    get_extract_graph_entities_prompt,
)
from jumo_server.memory.graph.tools import (
    ExtractEntitiesTool,
    ExtractGraphKnowledgeTool,
)


class GraphMemory:
    embedder = Embedder()

    async def process_message(self, message: Message):
        await self._extract_relationships(message)

    async def query_formatted(self, query: str):
        entities = await self.extract_entities(query)

        print(entities)

        found_entities = []

        if entities:
            for e in entities["entities"]:
                matches = await self.search(
                    entity_type=e["type"], entity_id=e["name"], limit=1
                )

                for match in matches:
                    found_entities.append(match["node"])

        entities_str = "\n\n".join(
            [self._format_entity(entity) for entity in found_entities]
        )

        prefix = (
            "## Knowledge Graph Information:\n\n"
            "Your knowledge graph system uses a graph database to store information about entities and their relationships. "
            "Entities and their relationships are extracted in a subconsious process and stored in the graph database. "
            "The results here are the result of a vector similarity search in the graph database entites extracted from the input query of the current message.\n\n"
            "### Entities:\n\n"
        )

        return prefix + entities_str

    def _format_entity(self, entity: dict[str, Any]):
        id = entity["id"]
        output = f"#### {id}:\n\n"

        for key, value in entity.items():
            if key == "embedding":
                continue
            output += f"{key}: {value}\n"

        return output

    async def search(self, entity_type: str, entity_id: str, limit: int = 10):
        search_embedding = await self.embedder.embed(
            entity_type + " " + entity_id, dimensions=256
        )

        async with graph_db.session() as session:
            res = await session.run(
                """
                MATCH (node:Entity)
                WITH node, vector.similarity.cosine(node.embedding, $embedding) AS score
                WHERE score > 0.9
                RETURN node, score
                ORDER BY score DESC LIMIT $limit;
                """,
                embedding=search_embedding,
                limit=limit,
            )

            return await res.data()

    async def _extract_relationships(self, message: Message):
        speaker = "Jumo" if message["role"] == "assistant" else "Ryan"

        result = await make_llm_tool_call(
            query=message["content"],
            tool=ExtractGraphKnowledgeTool(),
            system=get_extract_graph_entities_prompt(speaker),
        )

        if result:
            async with graph_db.session() as session:
                for entity in result["entities"]:
                    head_embedding = await self.embedder.embed(
                        entity["head_type"] + " " + entity["head"],
                        dimensions=256,
                    )

                    existing_head = await self.search(
                        entity["head_type"], entity["head"], limit=1
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
                        entity["tail_type"] + " " + entity["tail"],
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

    async def extract_entities(self, input: str):
        return await make_llm_tool_call(
            query=input,
            tool=ExtractEntitiesTool(),
            system=EXTRACT_ENTITIES_PROMPT,
            model="claude-3-5-haiku-latest",
        )
