from fastapi import APIRouter

import PyAPI.ResourceService as GIAPI


router = APIRouter(prefix="/api/aboutPage", tags=["About"])
ABOUT_SECTION_DIR = GIAPI.BASE_DIR / "AboutSection"


@router.get("/data")
async def get_about_page_data():
    return GIAPI.build_api_data_from_json(
        ABOUT_SECTION_DIR / "AboutSectionData.json",
        {
            "aboutPhotos": "/api/aboutPage/Image",
            "moreDetails.image": "/api/aboutPage/Image",
        },
    )


@router.get("/Image/{name}")
async def get_about_page_image(name: str):
    return GIAPI.create_image_response(ABOUT_SECTION_DIR / name, False)
