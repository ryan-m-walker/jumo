from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from jumo_server.db import memory_processing_queue
from jumo_server.db.graph_db import graph_db, init_graph_db
from jumo_server.db.qdrant import initialize_qdrant_client
from jumo_server.jumo import Jumo
from jumo_server.events import event_manager
from jumo_server.memory.episodic.db.episodic_memory_queue import (
    init_episodic_memory_queue,
)


load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await initialize_qdrant_client()
    await memory_processing_queue.init()
    await init_episodic_memory_queue()
    await graph_db.verify_connectivity()
    await init_graph_db()

    yield

    await graph_db.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello Jumo!"}


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
    jumo = Jumo()
    response = await jumo.prompt(body["input"])
    return {"response": response}


@app.post("/graph/search")
async def graph_search_handler():
    jumo = Jumo()
    result = await jumo._memory._graph_memory.search(
        entity_type="Person",
        entity_id="Ryan",
    )
    return result


@app.post("/system_prompt")
async def system_prompt(body: dict):
    jumo = Jumo()
    prompt = await jumo.get_system_prompt(body["query"])
    return {"prompt": prompt}
