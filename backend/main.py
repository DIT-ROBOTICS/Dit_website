from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.responses import FileResponse
import json,uvicorn,socket

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MEMBER_IMAGE_DIR = BASE_DIR / "static" / "members"


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


@app.get("/api/member_info/{member_type}")
async def get_members(member_type: str):
    info_path = {
        "Leader" : "Leadership.json",
        "Advisor" : "Advisors.json"
    }
    file_path = DATA_DIR / info_path.get(member_type)
    if not file_path:
        raise HTTPException(status_code=404, detail="Member info not found")
    with open(
        file_path,
        encoding="utf-8"
    ) as f:

        return json.load(f)

    
@app.get("/api/member_images/{image_type}/{member_id}")
async def get_member_image(image_type: str, member_id: int):
    image_path = {
        "Leader-image": "Leadership.json",
        "advisor-image": "Advisors.json"
    }
    file_path = DATA_DIR / image_path.get(image_type)
    if not file_path:
        raise HTTPException(status_code=404, detail="Member info not found")
    with open(file_path, encoding="utf-8") as f:
        members = json.load(f)

    member = next(
        (member for member in members if member["id"] == member_id),
        None
    )

    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    image_path = BASE_DIR / member["image"]

    if not image_path.is_file():
        raise HTTPException(status_code=404, detail="Member image not found")

    return FileResponse(image_path)


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