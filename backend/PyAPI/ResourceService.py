import json,re
from io import BytesIO
from pathlib import Path
from fastapi import HTTPException
from fastapi.responses import FileResponse,StreamingResponse
from PIL import Image

BASE_DIR = Path("/Users/jason/Desktop/我的程式/web_page_2/Dit_Official_Website/database")
DATA_DIR=BASE_DIR/"data"
ASSETS_DIR=BASE_DIR/"assets"




def get_file(file_path:Path):
    """回傳指定檔案，供 FastAPI 路由直接使用。

    Args:
        file_path: 要回傳的檔案路徑，必須是存在的實體檔案。

    Returns:
        FileResponse: FastAPI 的檔案回應；瀏覽器會依檔案類型顯示或下載。

    Raises:
        HTTPException: 路徑為空、檔案不存在或路徑不是檔案時回傳 HTTP 404。

    Example:
        在 APIRouter 中直接回傳圖片或文件::

            @router.get("/files/{name}")
            async def get_resource(name: str):
                return get_file(BASE_DIR / "files" / name)
    """
    if not file_path or not file_path.is_file():
        raise HTTPException(status_code=404,detail=f"{file_path}:File not found")
    return FileResponse(file_path)

def build_api_data(data,api_fields):
    """將資料中的檔名欄位轉換成可供前端請求的 API URL。

    此函式會直接修改傳入的 ``data``，不會建立深層副本。欄位路徑使用
    點號表示巢狀結構，例如 ``robots.imagePath``。路徑途中遇到陣列時，
    會自動處理陣列內的每個物件。

    Args:
        data: 從 JSON 讀取的 dict 或 list，也可以是相同結構的 Python 資料。
        api_fields: 欄位路徑與 API 基底 URL 的對照 dict。API 結尾有無斜線
            皆可，函式會自動整理。

    Returns:
        dict | list: 已完成 URL 轉換的原始資料物件。

    Notes:
        - 字串 ``"photo.jpg"`` 會轉成 ``"/api/images/photo.jpg"``。
        - 字串陣列中的每個非空值都會被轉換。
        - 空字串、非字串值及不存在的欄位會維持原樣。
        - 重複呼叫可能重複加上 API 前綴，因此同一份資料通常只處理一次。

    Example:
        轉換單一圖片與機器人陣列中的模型路徑::

            data = {
                "background": "team.jpg",
                "robots": [{"glbPath": "robot.glb"}],
            }
            result = build_api_data(data, {
                "background": "/api/images",
                "robots.glbPath": "/api/models",
            })

            # result["background"] == "/api/images/team.jpg"
            # result["robots"][0]["glbPath"] == "/api/models/robot.glb"
    """
    def add_api(data,path,api):
        """遞迴走訪指定欄位路徑，並在最終字串值前加上 API URL。"""
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
    """讀取 JSON 檔案，並將指定的檔名欄位轉成 API URL。

    這是 ``build_api_data()`` 的檔案版捷徑，適合直接在 FastAPI 路由中
    建立要回傳給前端的 JSON 資料。

    Args:
        file_path: JSON 檔案的完整路徑。
        api_fields: 欄位路徑與 API 基底 URL 的對照 dict；不需要轉換欄位時
            傳入空 dict ``{}``。

    Returns:
        dict | list: JSON 解析並完成 API URL 轉換後的資料。

    Raises:
        HTTPException: JSON 檔案不存在或路徑不是檔案時回傳 HTTP 404。
        json.JSONDecodeError: JSON 格式不合法時拋出解析錯誤。

    Example:
        讀取贊助商資料並轉換 logo 路徑::

            data = build_api_data_from_json(
                BASE_DIR / "SponsorSection" / "SponsorsData.json",
                {"logo": "/api/Sponsors/Image"},
            )
    """
    if not file_path or not file_path.is_file():
        raise HTTPException(status_code=404,detail="JSON file not found")

    with open(file_path,encoding="utf-8") as f:
        data=json.load(f)

    return build_api_data(data,api_fields)



def get_json_data(title:str):
    """依預先定義的名稱取得 JSON 原始檔案。

    Args:
        title: JSON 資源名稱。目前支援 ``"Links"`` 與 ``"AboutData"``。

    Returns:
        FileResponse: 對應 JSON 檔案的 FastAPI 回應。

    Raises:
        HTTPException: title 不在對照表內，或對應檔案不存在時，由
            ``get_file()`` 回傳 HTTP 404。

    Example:
        搭配動態路由使用::

            @app.get("/api/jsonData/{title}")
            async def json_data_api(title: str):
                return get_json_data(title)

        前端可請求 ``/api/jsonData/Links``。
    """
    file_name={
        "Links":BASE_DIR/"ContactSection/Linktree.json",
        "AboutData":BASE_DIR/"AboutSection/AboutSectionData.json"
    }.get(title)
    return get_file(file_name)



def create_image_response(image_path:Path,full:bool=False):
    """回傳原始圖片，或建立縮圖並以 WebP 串流回傳。

    Args:
        image_path: 要讀取的圖片檔案路徑。
        full: ``True`` 時直接回傳原始檔；``False`` 時將圖片限制在
            1600×1600 以內、保持長寬比，並轉為品質 80 的 WebP。

    Returns:
        FileResponse: ``full=True`` 時的原始圖片回應。
        StreamingResponse: ``full=False`` 時 media type 為 ``image/webp``
            的記憶體串流回應。

    Raises:
        FileNotFoundError: 圖片路徑不存在時可能由 Pillow 拋出。
        PIL.UnidentifiedImageError: 檔案不是 Pillow 可辨識的圖片時拋出。

    Example:
        預設回傳適合網頁載入的 WebP 縮圖::

            return create_image_response(image_dir / name)

        需要原圖時::

            return create_image_response(image_dir / name, full=True)
    """
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
    """依設定檔中的資源 key 回傳彈出視窗使用的檔案。

    函式會讀取 ``database/assets/item_name.json``，用 ``file`` 查出實際
    檔名，再從同一個 assets 資料夾回傳該檔案。這讓前端不需要知道磁碟
    上的真實檔名。

    Args:
        file: ``item_name.json`` 中定義的 key，例如
            ``"sponsorshipMethods"`` 或 ``"whiteSeeMore"``。

    Returns:
        FileResponse: key 所對應檔案的 FastAPI 回應。

    Raises:
        HTTPException: 設定檔不存在、key 不存在或目標檔案不存在時回傳
            HTTP 404。
        json.JSONDecodeError: ``item_name.json`` 格式不合法時拋出解析錯誤。

    Example:
        路由設定::

            @app.get("/api/PopUpItem/{file}")
            async def get_pop_up_file(file: str):
                return get_pop_up_item(file)

        前端可請求 ``/api/PopUpItem/sponsorshipMethods``。
    """
    POP_UP_JSON=ASSETS_DIR/"item_name.json"
    items=build_api_data_from_json(POP_UP_JSON,{})

    filename=items.get(file)

    if not filename:
        raise HTTPException(status_code=404,detail="Pop up item not found")

    file_path=ASSETS_DIR/filename
    return get_file(file_path)
