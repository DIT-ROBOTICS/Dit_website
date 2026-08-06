from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn,socket


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/team")
async def get_team():
    return {
        "name": "PME TEAM",
        "slogan": "Create · Explore · Connect",
        "description": (
            "我們是一群喜歡設計、程式與創意實驗的夥伴。"
        ),
    }


@app.get("/api/members")
async def get_members():
    return [
        {
            "id": 1,
            "name": "Jason",
            "role": "Frontend Developer",
            "image": "/members/member-1.jpg",
        },
        {
            "id": 2,
            "name": "Alice",
            "role": "Visual Designer",
            "image": "/members/member-2.jpg",
        },
    ]

def get_local_ip() -> str:
    """
    獲取當前電腦在局域網（Wi-Fi）中的 IP 地址
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 💡 核心防守魔法：這裡並不會真的發送封包，只是藉由嘗試連線 
        # 逼作業系統的大腦吐出目前正在工作中的網卡物理 IP
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    except Exception:
        # 萬一完全沒連網，就給回本地迴圈地址
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip

print(f"ip:${get_local_ip()}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # 💡 關鍵防守：全面開放區域網路，讓手機連得進來
        port=8000,  # 💡 配合你原本的習慣，我們直接佔領 8000 Port
        reload=True,
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem",
    )