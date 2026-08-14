import json,re
from io import BytesIO
from pathlib import Path
from fastapi import HTTPException
from fastapi.responses import FileResponse,StreamingResponse
from PIL import Image

BASE_DIR=Path(__file__).resolve().parent.parent
DATA_DIR=BASE_DIR/"data"

def natural_sort_key(path):
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r'(\d+)', path.name)
    ]


def load_json(file_path:Path):
    if not file_path.is_file():
        raise HTTPException(status_code=404,detail="JSON file not found")

    with open(file_path,encoding="utf-8") as f:
        return json.load(f)


def get_json_data(title:str):
    file_name={
        "Links":"Linktree.json",
        "AboutData":"AboutSectionData.json"
    }.get(title)

    if file_name is None:
        raise HTTPException(status_code=404,detail="JSON data not found")

    return load_json(DATA_DIR/file_name)


def get_member_data(member_type:str):
    file_name={
        "Leader":"Leadership.json",
        "Advisor":"Advisors.json"
    }.get(member_type)

    if file_name is None:
        raise HTTPException(status_code=404,detail="Member info not found")

    return load_json(DATA_DIR/file_name)


def get_member_by_id(member_type:str,member_id:int):
    members=get_member_data(member_type)

    member=next(
        (member for member in members if member["id"]==member_id),
        None
    )

    if member is None:
        raise HTTPException(status_code=404,detail="Member not found")

    return member


def get_member_image_path(image_type:str,member_id:int):
    member_type={
        "Leader-image":"Leader",
        "advisor-image":"Advisor"
    }.get(image_type)

    if member_type is None:
        raise HTTPException(status_code=404,detail="Image type not found")

    member=get_member_by_id(member_type,member_id)
    image_path=BASE_DIR/member["image"]

    if not image_path.is_file():
        raise HTTPException(status_code=404,detail="Member image not found")

    return image_path


def get_other_image_path(image_type:str,path:str):
    folder={
        "competition":"static/Competition_image",
        "aboutPageImages":"static/AboutPhoto"
    }.get(image_type)

    if folder is None:
        raise HTTPException(status_code=404,detail="Folder not found")

    file_path=BASE_DIR/folder/path

    if not file_path.is_file():
        raise HTTPException(status_code=404,detail="Image not found")

    return file_path


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


def get_about_page_images():
    folder_path=BASE_DIR/"static"/"AboutPhoto"

    if not folder_path.is_dir():
        raise HTTPException(status_code=404,detail="Image folder not found")

    images=sorted(
        [
            file
            for file in folder_path.iterdir()
            if file.is_file()
            and file.suffix.lower() in {".jpg",".jpeg",".png",".webp",".gif"}
        ],
        key=natural_sort_key
    )

    return [
        f"/api/other_images/aboutPageImages/{file.name}"
        for file in images
    ]
