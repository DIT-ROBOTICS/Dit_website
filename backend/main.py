from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn,socket
import PyAPI.ResourceService as GIAPI
from routers import *
from typing import Literal

BASE_DIR = Path("/Users/jason/Desktop/我的程式/web_page_2/Dit_Official_Website/database")


app = FastAPI()

@app.middleware("http")
async def log_requests(request:Request,call_next):
    client_ip=request.headers.get("cf-connecting-ip")
    if not client_ip:
        forwarded=request.headers.get("x-forwarded-for")
        if forwarded:
            client_ip=forwarded.split(",")[0].strip()

    if not client_ip:
        client_ip=request.client.host if request.client else "unknown"
    print(f"[REQUEST] {client_ip} -> {request.method} {request.url.path}")
    response=await call_next(request)
    print(f"[RESPONSE] {client_ip} <- {response.status_code} {request.url.path}")
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(advisor_router)
app.include_router(about_router)
app.include_router(eurobot_router)
app.include_router(sponsors_router)


@app.get("/api/jsonData/{title}")
async def json_data_api(title:str):
    return GIAPI.get_json_data(title)

@app.get("/api/PopUpItem/{file}")
async def get_pop_up_item(file:str):
    return GIAPI.get_pop_up_item(file)


@app.get("/api/heroVideo/{platform}")
async def get_hero_video(platform:Literal["Mobile","Desktop"]):
    HEROVIDEO_DIR = BASE_DIR / "HeroVideo"
    file_path = HEROVIDEO_DIR / "VideoInfo.json"
    data=GIAPI.build_api_data_from_json(file_path,{})
    return GIAPI.get_file(HEROVIDEO_DIR/data[platform])

    



def get_local_ip() -> str:
    """
    獲取當前電腦在局域網（Wi-Fi）中的 IP 地址
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip


if __name__ == "__main__":
    print(f"ip:{get_local_ip()}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # 💡 關鍵防守：全面開放區域網路，讓手機連得進來
        port=8000,  # 💡 配合你原本的習慣，我們直接佔領 8000 Port
        reload=True,
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem",
    )
