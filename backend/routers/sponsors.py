from fastapi import APIRouter

import PyAPI.ResourceService as GIAPI


router = APIRouter(prefix="/api/Sponsors", tags=["Sponsors"])
SPONSORS_DIR = GIAPI.BASE_DIR / "SponsorSection"


@router.get("")
async def get_sponsors_data():
    return GIAPI.build_api_data_from_json(
        SPONSORS_DIR / "SponsorsData.json",
        {"sponsors.logo": "/api/Sponsors/Image"},
    )


@router.get("/Image/{filename:path}")
async def get_sponsor_image(filename: str):
    return GIAPI.get_file(SPONSORS_DIR / "icon" / filename)

