from typing import Optional

from fastapi import APIRouter

import PyAPI.EurobotAPI as Eurobot
import PyAPI.ResourceService as GIAPI


router = APIRouter(prefix="/api/Eurobot", tags=["Eurobot"])


@router.get("/Introduction")
async def get_eurobot_introduction():
    return GIAPI.get_file(Eurobot.EUROBOT_DIR / "EurobotIntroduction.txt")


@router.get("/History")
async def get_eurobot_history():
    return Eurobot.get_all_eurobot_data()


@router.get("/History/Background")
async def get_eurobot_background():
    folder = Eurobot.EUROBOT_DIR / "ArchiveBackground"
    first_file = next((file for file in folder.iterdir() if file.is_file()), None)
    return GIAPI.get_file(first_file)


@router.get("/{year}/file/{filename}")
async def get_eurobot_file(year: int, filename: str):
    return GIAPI.get_file(Eurobot.EUROBOT_DIR / str(year) / filename)


@router.get("")
@router.get("/{year}")
async def get_eurobot(year: Optional[int] = None):
    if year is not None:
        return Eurobot.load_eurobot(year)
    return Eurobot.load_eurobot(Eurobot.get_latest_year())
