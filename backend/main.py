from fastapi import FastAPI, HTTPException, Query,Request
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.responses import FileResponse
import uvicorn,socket,json
import PyAPI.EurobotAPI as Eurobot
import PyAPI.GetItemAPI as GIAPI
from typing import Literal,Optional

BASE_DIR = Path("/Users/jason/Desktop/我的程式/web_page_2/Dit_Official_Website/database")
DATA_DIR = BASE_DIR / "data"
MEMBER_IMAGE_DIR = BASE_DIR / "MemberSection/members"
SPONSORS_LOGO_DIR = BASE_DIR / "SponsorSection"
HEROVIDEO_DIR = BASE_DIR / "HeroVideo"


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


@app.get("/api/jsonData/{title}")
async def json_data_api(title:str):
    return GIAPI.get_json_data(title)

@app.get("/api/Advisor/data")
async def Advisor_data():
    Advisor_dir = BASE_DIR/"AdvisorSection"
    return GIAPI.build_api_data_from_json(Advisor_dir/"Advisors.json",{
            "image":"/api/Advisor/Image",
        })
@app.get("/api/Advisor/Image/{name}")
async def Advisor_Image(name:str):
    Advisor_dir = BASE_DIR/"AdvisorSection"
    return GIAPI.create_image_response(Advisor_dir/name,False)



@app.get("/api/member_info/{member_type}")
async def member_info_api(member_type:str):
    return GIAPI.get_member_data(member_type)


@app.get("/api/member_images/{image_type}/{member_id}")
async def member_image_api(image_type:str, member_id:int, full:bool=Query(False)):
    image_path=GIAPI.get_member_image_path(image_type,member_id)
    return GIAPI.create_image_response(image_path,full)


@app.get("/api/other_images/{image_type}/{path:path}")
async def other_image_api(image_type:str, path:str, full:bool=Query(False)):
    image_path=GIAPI.get_other_image_path(image_type,path)
    return GIAPI.create_image_response(image_path,full)


@app.get("/api/aboutPage/data")
async def about_page_data():
    about_dir = BASE_DIR/"AboutSection"
    return GIAPI.build_api_data_from_json(about_dir/"AboutSectionData.json",{
            "AboutPhoto":"/api/aboutPage/Image",
            "MoreDetail.image":"/api/aboutPage/Image",
        })
@app.get("/api/aboutPage/Image/{name}")
async def about_page_Image(name:str):
    about_dir = BASE_DIR/"AboutSection"
    return GIAPI.create_image_response(about_dir/name,False)


@app.get("/api/PopUpItem/{file}")
async def get_pop_up_item(file:str):
    return GIAPI.get_pop_up_item(file)


@app.get("/api/Eurobot")
@app.get("/api/Eurobot/{year}")
async def get_eurobot(year:Optional[int]=None):
    if year: return Eurobot.load_eurobot(year)
    return Eurobot.load_eurobot(Eurobot.get_latest_year())

@app.get("/api/Eurobot/Introduction")
async def get_eurobot_introduction():
    file_path=Eurobot.EUROBOT_DIR/"EurobotIntroduction.txt"
    return GIAPI.get_file(file_path)

@app.get("/api/Eurobot/History")
async def get_eurobot_history():
    return Eurobot.get_all_eurobot_api()

@app.get("/api/Eurobot/History/Background")
async def get_eurobot_Background():
    folder=Eurobot.EUROBOT_DIR/"ArchiveBackground"
    first_file=next((f for f in folder.iterdir() if f.is_file()),None)
    return GIAPI.get_file(first_file)


@app.get("/api/Eurobot/{year}/file/{filename}")
async def get_eurobot_file(year:int,filename:str):
    file_path=Eurobot.EUROBOT_DIR/str(year)/filename
    return GIAPI.get_file(file_path)

@app.get("/api/Sponsors")
async def get_Sponsors_Data():
    return GIAPI.build_api_data_from_json(SPONSORS_LOGO_DIR/"SponsorsData.json",{
        "logo":"/api/Sponsors/Logo"
    })


@app.get("/api/Sponsors/Logo/{filename:path}")
async def get_Sponsors_Logo(filename:str):
    file_path=SPONSORS_LOGO_DIR/"icon"/filename
    return GIAPI.get_file(file_path)


@app.get("/api/heroVideo/{platform}")
async def get_hero_video(platform:Literal["Mobile","Desktop"]):
    file_path = HEROVIDEO_DIR / "VideoInfo.json"
    with open(file_path,"r",encoding="utf-8") as f:
        data=json.load(f)
    if data[platform]:
        return FileResponse(HEROVIDEO_DIR / data[platform])
    raise HTTPException(status_code=404,detail="File not found")

    



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