import asyncio
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

clients = set()

# =========================
# 🚀 游戏逻辑
# =========================
class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.multiplier = 1.0
        self.crash = round(random.uniform(1.5, 10), 2)

game = Game()

# =========================
# 🌐 首页（关键！解决 Not Found）
# =========================
@app.get("/")
def home():
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>Lucky Rocket</title>
    <style>
        body {
            margin: 0;
            background: #0b0f1a;
            color: white;
            text-align: center;
            font-family: Arial;
        }
        #m {
            font-size: 80px;
            color: #00ffcc;
            margin-top: 120px;
        }
    </style>
</head>
<body>

<h1>🚀 Lucky Rocket</h1>
<div id="m">1.00x</div>

<script>
let ws = new WebSocket("wss://lucky-rocket-web.onrender.com/ws");

ws.onmessage = (e) => {
    let d = JSON.parse(e.data);
    if (d.type === "tick") {
        document.getElementById("m").innerText = d.m + "x";
    }
};
</script>

</body>
</html>
""")

# =========================
# 🌐 WebSocket
# =========================
@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.discard(websocket)

# =========================
# 📡 广播
# =========================
async def broadcast(data):
    for ws in list(clients):
        try:
            await ws.send_json(data)
        except:
            clients.discard(ws)

# =========================
# 🚀 游戏循环
# =========================
async def loop():
    while True:
        game.reset()

        while game.multiplier < game.crash:
            await asyncio.sleep(0.3)
            game.multiplier += 0.05
            game.multiplier = round(game.multiplier, 2)

            await broadcast({
                "type": "tick",
                "m": game.multiplier
            })

        await asyncio.sleep(3)

@app.on_event("startup")
async def startup():
    asyncio.create_task(loop())
