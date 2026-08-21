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

def get_all_eurobot_data():
    years=[ int(item.name)
            for item in EUROBOT_DIR.iterdir()
            if item.is_dir() and item.name.isdigit() ]
    years.sort()
    return [load_eurobot(year) for year in years[:-1]]
    


def load_eurobot(year:int):
    folder=EUROBOT_DIR/str(year)
    json_path=folder/"main_data.json"
    data=GIAPI.build_api_data_from_json(json_path,{})

    for robot in data.get("robots",[]):
        glb_filename=robot.get("glbPath")
        glb_file=folder/glb_filename if glb_filename else None
        robot["glbSize"]=glb_file.stat().st_size if glb_file and glb_file.is_file() else 0

    return GIAPI.build_api_data(data,{
        "background":f"/api/Eurobot/{year}/file",
        "venueImage":f"/api/Eurobot/{year}/file",
        "robots.glbPath":f"/api/Eurobot/{year}/file",
        "robots.imagePath":f"/api/Eurobot/{year}/file",
        "robots.viewerBackground":f"/api/Eurobot/{year}/file",
        "robots.moreDetailsPath":f"/api/Eurobot/{year}/file"
    })
