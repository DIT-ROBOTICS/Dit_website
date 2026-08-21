from fastapi import APIRouter

import PyAPI.ResourceService as GIAPI


router = APIRouter(prefix="/api/Advisor", tags=["Advisor"])
ADVISOR_SECTION_DIR = GIAPI.BASE_DIR / "AdvisorSection"


@router.get("/data")
async def get_advisor_data():
    return GIAPI.build_api_data_from_json(
        ADVISOR_SECTION_DIR / "Advisors.json",
        {"image": "/api/Advisor/Image"},
    )


@router.get("/Image/{name}")
async def get_advisor_image(name: str):
    return GIAPI.create_image_response(ADVISOR_SECTION_DIR / name, False)

