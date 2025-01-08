import uuid
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from jumo_server.db.qdrant import initialize_qdrant_client, insert_vector, search_vector
from jumo_server.db.messages import get_messages
from jumo_server.embeddings import create_embedding
from jumo_server.memory import memory_client
from jumo_server.chat import chat
from jumo_server.db.messages import messages_collection
from jumo_server.events import event_manager
from jumo_server.memory.manager import memory_manager


load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await initialize_qdrant_client()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello Jumo!"}


@app.get("/transcript")
async def transcript():
    messages = (
        messages_collection.find({}).limit(
            10).sort([("created_at", -1)]).to_list()
    )

    # stringify the ObjectId
    for message in messages:
        message["_id"] = str(message["_id"])

    return messages


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket):
    await event_manager.connect(websocket)

    try:
        while True:
            # Keep the connection alive and handle any incoming messages
            _ = await websocket.receive_text()

    except WebSocketDisconnect:
        await event_manager.disconnect(websocket)


@app.post("/chat")
async def send_chat_message(body: dict):
    return await chat(body["input"])


@app.post("/memories/test")
async def test_memory(body: dict):
    return memory_client().search(query = body["query"], user_id="test_user")


@app.post('/embedding/create')
async def embedding_create(body: dict):
    text = body["input"]
    id = str(uuid.uuid4())

    embedding = await create_embedding(text)
    result = await insert_vector(vector_id=id, vector=embedding, text=text)

    return result


@app.post('/embedding/search')
async def embedding_search(body: dict):
    text = body["input"]

    embedding = await create_embedding(text)
    result = await search_vector(vector=embedding)

    return result


@app.post('/memory/create')
async def memory_create(body: dict):
    print(body['input'])
    messages = await get_messages(limit=10)
    return await memory_manager.process_batch(messages)
