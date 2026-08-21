import json,re
from io import BytesIO
from pathlib import Path
from fastapi import HTTPException
from fastapi.responses import FileResponse,StreamingResponse
from PIL import Image

BASE_DIR = Path("/Users/jason/Desktop/我的程式/web_page_2/Dit_Official_Website/database")
DATA_DIR=BASE_DIR/"data"
ASSETS_DIR=BASE_DIR/"assets"

def natural_sort_key(path):
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r'(\d+)', path.name)
    ]


def get_file(file_path:Path):
    if not file_path or not file_path.is_file():
        raise HTTPException(status_code=404,detail=f"{file_path}:File not found")
    return FileResponse(file_path)

def build_api_data(data,api_fields):
    def add_api(data,path,api):
        if not path: return

        key=path[0]

        if isinstance(data,list):
            for item in data:
                add_api(item,path,api)
            return

        if not isinstance(data,dict) or key not in data: return

        if len(path)>1:
            add_api(data[key],path[1:],api)
            return

        value=data[key]
        base=api.rstrip("/")

        if isinstance(value,list):
            data[key]=[f"{base}/{item}" if isinstance(item,str) and item else item for item in value]
        elif isinstance(value,str) and value:
            data[key]=f"{base}/{value}"

    for path,api in api_fields.items():
        add_api(data,path.split("."),api)

    # print(data)
    return data

def build_api_data_from_json(file_path:Path,api_fields:dict):
    if not file_path or not file_path.is_file():
        raise HTTPException(status_code=404,detail="JSON file not found")

    with open(file_path,encoding="utf-8") as f:
        data=json.load(f)

    return build_api_data(data,api_fields)



def get_json_data(title:str):
    file_name={
        "Links":BASE_DIR/"ContactSection/Linktree.json",
        "AboutData":BASE_DIR/"AboutSection/AboutSectionData.json"
    }.get(title)
    return get_file(file_name)



def create_image_response(image_path:Path,full:bool=False):
    if full:
        return FileResponse(image_path)

    with Image.open(image_path) as img:
        img.thumbnail((1600,1600))
        buffer=BytesIO()
        img.save(buffer,format="WEBP",quality=80)

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="image/webp"
    )




def get_pop_up_item(file:str):
    POP_UP_JSON=ASSETS_DIR/"item_name.json"
    items=build_api_data_from_json(POP_UP_JSON,{})

    filename=items.get(file)

    if not filename:
        raise HTTPException(status_code=404,detail="Pop up item not found")

    file_path=ASSETS_DIR/filename
    return get_file(file_path)