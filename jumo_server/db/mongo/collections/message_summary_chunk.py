from datetime import datetime
from pymongo.asynchronous.collection import AsyncCollection
from typing_extensions import Literal, NotRequired, TypedDict

from jumo_server.db.mongo import db
from jumo_server.db.mongo.collections import MessageSummary


MessageSummaryChunkStatus = Literal["pending", "completed", "error"]


class MessageSummaryChunk(TypedDict):
    status: MessageSummaryChunkStatus
    summary: str
    start: datetime
    end: datetime
    summaries: list[MessageSummary]
    created_at: datetime
    completed_at: NotRequired[datetime]


class MessageSummaryChunkCollection:
    _collection: AsyncCollection[MessageSummaryChunk] = db["message_summary_chunk"]
