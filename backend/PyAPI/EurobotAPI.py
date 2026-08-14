import json
from pathlib import Path
from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse

app=FastAPI()
BASE_DIR=Path(__file__).resolve().parent.parent
EUROBOT_DIR=BASE_DIR/"data"/"Eurobot"

def get_latest_year():
    years=[
        int(item.name)
        for item in EUROBOT_DIR.iterdir()
        if item.is_dir() and item.name.isdigit()
    ]
    return max(years)

def load_eurobot(year:int):
    folder=EUROBOT_DIR/str(year)
    json_path=folder/"main_data.json"

    if not json_path.is_file():
        raise HTTPException(status_code=404,detail="Eurobot data not found")

    with open(json_path,"r",encoding="utf-8") as f:
        data=json.load(f)

    data["Background"]=f"/api/Eurobot/{year}/file/{data['Background']}"

    for robot in data["Robot_Data"]:
        robot["glbPath"]=f"/api/Eurobot/{year}/file/{robot['glbPath']}"
        robot["imagePath"]=f"/api/Eurobot/{year}/file/{robot['imagePath']}"
        robot["View3DBackground"]=f"/api/Eurobot/{year}/file/{robot['View3DBackground']}"
        robot["SeeMoreImagePath"]=f"/api/Eurobot/{year}/file/{robot['SeeMoreImagePath']}"

    return data