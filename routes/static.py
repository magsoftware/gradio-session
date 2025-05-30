from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/manifest.json")
async def manifest():
    return FileResponse("static/manifest.json")