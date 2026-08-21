import json
from pathlib import Path
from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse
import PyAPI.GetItemAPI as GIAPI

app=FastAPI()
BASE_DIR = Path("/Users/jason/Desktop/我的程式/web_page_2/Dit_Official_Website/database")
EUROBOT_DIR=BASE_DIR/"Eurobot"

def get_latest_year():
    years=[
        int(item.name)
        for item in EUROBOT_DIR.iterdir()
        if item.is_dir() and item.name.isdigit()
    ]
    return max(years)

def get_all_eurobot_api():
    years=[
            int(item.name)
            for item in EUROBOT_DIR.iterdir()
            if item.is_dir() and item.name.isdigit()
        ]
    years.sort()
    api = [
                f"/api/Eurobot/{y}"
                for y in years
            ]
    return api[:-1]
    


def load_eurobot(year:int):
    folder=EUROBOT_DIR/str(year)
    json_path=folder/"main_data.json"

    if not json_path.is_file():
        raise HTTPException(status_code=404,detail="Eurobot data not found")

    with open(json_path,encoding="utf-8") as f:
        data=json.load(f)

    for robot in data.get("Robot_Data",[]):
        glb_filename=robot.get("glbPath")
        glb_file=folder/glb_filename if glb_filename else None
        robot["glbSize"]=glb_file.stat().st_size if glb_file and glb_file.is_file() else 0

    return GIAPI.build_api_data(data,{
        "Background":f"/api/Eurobot/{year}/file",
        "VenueImage":f"/api/Eurobot/{year}/file",
        "Robot_Data.glbPath":f"/api/Eurobot/{year}/file",
        "Robot_Data.imagePath":f"/api/Eurobot/{year}/file",
        "Robot_Data.View3DBackground":f"/api/Eurobot/{year}/file",
        "Robot_Data.SeeMoreImagePath":f"/api/Eurobot/{year}/file"
    })