from datetime import datetime
from bson.objectid import ObjectId
from typing_extensions import Literal, TypedDict


class GraphMemoryQueue(TypedDict):
    _id: ObjectId
    user_id: str
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime
    system_prompt: str | None


# messages_collection: AsyncCollection[] = db["messages"]
