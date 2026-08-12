from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.responses import FileResponse, StreamingResponse
import json,uvicorn,socket,re
from PIL import Image
from io import BytesIO

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



def natural_sort_key(path):
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r'(\d+)', path.name)
    ]


@app.get("/api/team")
async def get_team():
    return {
        "name": "PME TEAM",
        "slogan": "Create · Explore · Connect",
        "description": (
            "我們是一群喜歡設計、程式與創意實驗的夥伴。"
        ),
    }

@app.get("/api/Links")
async def get_links():
    file_path = DATA_DIR / "Linktree.json"
    if not file_path:
        raise HTTPException(status_code=404, detail="Links not found")
    with open(
        file_path,
        encoding="utf-8"
    ) as f:
        return json.load(f)


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
async def get_member_image(image_type: str, member_id: int,full: bool = Query(False)):
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

    if full:
        return FileResponse(image_path)
    img = Image.open(image_path)
    img.thumbnail((1600, 1600))
    buffer = BytesIO()
    img.save(buffer, format="WEBP", quality=80)
    buffer.seek(0)
    return StreamingResponse(buffer,media_type="image/webp")


@app.get("/api/other_images/{image_type}/{path:path}")
async def get_other_image(image_type: str, path: str,full: bool = Query(False)):
    image_path = {
        "competition": "static/Competition_image/",
        "aboutPageImages": "static/AboutPhoto/"
    }
    file_path = BASE_DIR / image_path.get(image_type) / path
    if not file_path:
        raise HTTPException(status_code=404, detail="Folder not found")
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    if full:
        return FileResponse(file_path)
    img = Image.open(file_path)
    img.thumbnail((1600, 1600))
    buffer = BytesIO()
    img.save(buffer, format="WEBP", quality=80)
    buffer.seek(0)
    return StreamingResponse(buffer,media_type="image/webp")



@app.get("/api/aboutPageImages")
async def get_aboutPageImages():
    folder_path = BASE_DIR / "static" / "AboutPhoto"
    images = sorted(
                    [
                        file
                        for file in folder_path.iterdir()
                        if file.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif"}
                    ],
                    key=natural_sort_key
                )
    if not folder_path.is_dir():
        raise HTTPException(status_code=404, detail="Image not found")
    l = [ f"/api/other_images/aboutPageImages/{file.name}"  for file in images ]
    print(f"l:{l}")
    return l


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