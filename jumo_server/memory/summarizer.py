from datetime import datetime
from typing_extensions import TypedDict
import uuid
from bson.objectid import ObjectId
from anthropic.types.tool_param import ToolParam
from qdrant_client.models import PointStruct

from jumo_server.db.mongo.collections import (
    Message,
    message_summary_chunk_collection,
    message_summary_collection,
    message_summary_queue_collection,
)
from jumo_server.db.mongo.collections.message_summaries import MessageSummary
from jumo_server.db.mongo.collections.message_summary_chunks import MessageSummaryChunk
from jumo_server.db.qdrant import qdrant_client
from jumo_server.db.qdrant import SUMMARY_DB_COLLECTION
from jumo_server.embeddings import Embedder
from jumo_server.llm.llm import make_llm_tool_call
from jumo_server.tools.tool import Tool


def get_system_prompt(speaker: str):
    return "".join(
        [
            "You are an expert summarizer summarizing messages in a conversation between a user and an AI assistant named JUMO. ",
            "The message you will be summarizing will be from the user or the AI assistant. ",
            f"The current message you will be summarizing will be from {speaker}. ",
            "Any references to 'me', 'I' or any other references by the user to the self should be assumed to be referencing {speaker}. ",
            "The summary should be a concise and accurate representation of the message. ",
            "Capture the essence of the message and avoid any unnecessary details. ",
            "Make sure to capture all the important details of the message.\n",
            "This summary will be shown chronologically in the conversation history\n\n",
            "Things to consider:\n",
            "- What things were discussed?\n",
            "- What was the main point of the message?\n",
            "- What was the user or AI assistant trying to convey?\n",
            "- What factual information was shared?\n",
            "- What was the tone of the message?\n",
            "- Where there any more subtle events such as developments in relationships or growth in understanding of each participant or themselves?\n\n",
            "Please only output the summary and no other commentary. Do not respond to the messages themselves as the sender will not see your response.",
        ]
    )


class SummaryToolInput(TypedDict):
    summary: str


class SummaryTool(Tool[SummaryToolInput, str]):
    name = "summarize"
    description = "Write a summary for the given message."

    def json(self) -> ToolParam:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                    },
                },
            },
        }

    async def impl(self, input: SummaryToolInput) -> str:
        return input["summary"]


class Summarizer:
    _embedder = Embedder()

    async def process_message(self, message: Message):
        summary = await self._summarize_message(message)

        if not summary:
            return

        speaker = "Jumo" if message["role"] == "assistant" else "Ryan"

        summary_document: MessageSummary = {
            "_id": ObjectId(),
            "content": summary,
            "created_at": datetime.now(),
            "message_id": message["_id"],
            "speaker": speaker,
        }

        await message_summary_collection.save_message_summary(summary_document)
        await message_summary_queue_collection.push(summary_document)

        if await message_summary_queue_collection.check():
            summaries = await message_summary_queue_collection.empty()
            await self._process_queue(summaries)

    async def _summarize_message(self, message: Message):
        speaker = "Jumo" if message["role"] == "assistant" else "Ryan"

        query = f"Please summarize the following message from {speaker}:\n\n{message['content']}"

        summary = await make_llm_tool_call(
            tool=SummaryTool(),
            query=query,
            system=get_system_prompt(speaker),
        )

        if not summary:
            return

        return summary

    async def _process_queue(self, summaries: list[MessageSummary]):
        summaries_content = [summary["content"] for summary in summaries]
        text = "\n".join(summaries_content)

        chunk: MessageSummaryChunk = {
            "_id": ObjectId(),
            "status": "pending",
            "text": text,
            "start": summaries[-1]["created_at"],
            "end": summaries[0]["created_at"],
            "summaries": summaries,
            "created_at": datetime.now(),
        }

        await message_summary_chunk_collection.insert(chunk)

        vector_id = str(uuid.uuid4())
        vector = await self._embedder.embed(text)

        await qdrant_client.upsert(
            collection_name=SUMMARY_DB_COLLECTION,
            points=[
                PointStruct(
                    id=vector_id,
                    vector=vector,
                    payload={
                        "text": chunk["text"],
                        "chunk_id": str(chunk["_id"]),
                    },
                )
            ],
        )

        await message_summary_chunk_collection.complete(chunk["_id"])

    async def get_formatted(self, limit: int = 100) -> str:
        recent_summaries = await message_summary_collection.get_message_summaries(limit)

        if not recent_summaries:
            return ""

        output = (
            "## Conversation Summary:\n\n"
            f"This is the summary of the conversation so far for the past {limit} messages.\n\n"
        )

        for summary in recent_summaries:
            timestamp = summary["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            output += f"### {summary['speaker']} - {timestamp}\n\n"
            output += f"{summary['content']}\n\n"

        return output
