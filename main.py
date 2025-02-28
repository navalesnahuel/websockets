import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

clients: list[dict[str, WebSocket]] = []
chat_history: list[dict[str, str]] = []


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Aceptar la conexión WebSocket

    # Enviar el mensaje de solicitud de nombre de usuario
    await websocket.send_text(json.dumps({"message": "Enter your username:"}))

    # Recibir el nombre de usuario del cliente
    username = await websocket.receive_text()
    clients.append(
        {"username": username, "websocket": websocket}
    )  # Guardar el nombre y WebSocket

    # Enviar todo el historial de mensajes al nuevo cliente
    for message in chat_history:
        await websocket.send_text(
            json.dumps(message)
        )  # Enviar cada mensaje al nuevo cliente

    try:
        while True:
            # Recibir un mensaje del cliente
            message = await websocket.receive_text()
            print(f"Received message from {username}: {message}")

            # Crear el mensaje a transmitir
            message_data = {"username": username, "message": message}
            chat_history.append(message_data)  # Guardar el mensaje en el historial

            # Broadcast el mensaje a todos los clientes, incluido el remitente
            for client in clients:
                await client["websocket"].send_text(
                    json.dumps(message_data)
                )  # Enviar el mensaje a todos

    except WebSocketDisconnect:
        # Eliminar al cliente de la lista cuando se desconecte
        clients.remove({"username": username, "websocket": websocket})
        print(f"{username} disconnected.")
