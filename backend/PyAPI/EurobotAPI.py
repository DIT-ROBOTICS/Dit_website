import json
from pathlib import Path
from fastapi import HTTPException
import PyAPI.ResourceService as GIAPI

EUROBOT_DIR=GIAPI.BASE_DIR/"Eurobot"

def get_latest_year():
    years=[
        int(item.name)
        for item in EUROBOT_DIR.iterdir()
        if item.is_dir() and item.name.isdigit() ]
    return max(years)

def get_all_eurobot_api():
    years=[ int(item.name)
            for item in EUROBOT_DIR.iterdir()
            if item.is_dir() and item.name.isdigit() ]
    years.sort()
    api = [ f"/api/Eurobot/{y}" for y in years ]
    return api[:-1]
    


def load_eurobot(year:int):
    folder=EUROBOT_DIR/str(year)
    json_path=folder/"main_data.json"
    data=GIAPI.build_api_data_from_json(json_path,{})

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