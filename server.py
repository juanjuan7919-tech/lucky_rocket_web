import asyncio
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

clients = set()

# =========================
# 🚀 游戏核心
# =========================
class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.multiplier = 1.0
        self.crash = self.generate_crash()

    def generate_crash(self):
        r = random.random()
        crash = (1 / (1 - r + 0.01)) * 0.95
        return round(max(1.2, min(crash, 30)), 2)

game = Game()

# =========================
# 📡 广播
# =========================
async def broadcast(data):
    dead = []

    for ws in list(clients):
        try:
            await ws.send_json(data)
        except:
            dead.append(ws)

    for d in dead:
        clients.discard(d)

# =========================
# 🌐 WebSocket
# =========================
@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.discard(websocket)

# =========================
# 🚀 游戏循环
# =========================
async def game_loop():
    while True:
        game.reset()

        await broadcast({
            "type": "start",
            "crash": game.crash
        })

        while game.multiplier < game.crash:
            await asyncio.sleep(0.3)
            game.multiplier += 0.05
            game.multiplier = round(game.multiplier, 2)

            await broadcast({
                "type": "tick",
                "m": game.multiplier
            })

        await broadcast({
            "type": "crash",
            "crash": game.crash
        })

        await asyncio.sleep(3)

# =========================
# 🚀 启动
# =========================
@app.on_event("startup")
async def startup():
    asyncio.create_task(game_loop())
