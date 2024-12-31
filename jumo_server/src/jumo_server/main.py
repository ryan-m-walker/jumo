from dotenv import load_dotenv

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from jumo_server.chat import chat
from jumo_server.db.mongo import messages_collection
from jumo_server.events import event_manager


load_dotenv()

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello Jumo!"}


@app.get("/transcript")
async def transcript():
    messages = (
        messages_collection.find({}).limit(10).sort([("created_at", -1)]).to_list()
    )

    # stringify the ObjectId
    for message in messages:
        message["_id"] = str(message["_id"])

    return messages


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await event_manager.connect(websocket, client_id)

    try:
        while True:
            # Keep the connection alive and handle any incoming messages
            _ = await websocket.receive_text()
            # You can process incoming messages here if needed

    except WebSocketDisconnect:
        await event_manager.disconnect(websocket, client_id)


@app.post("/chat")
async def send_chat_message(body: dict):
    return await chat(body["input"])
