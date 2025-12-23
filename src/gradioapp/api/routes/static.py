from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

BASE_DIR = Path(__file__).parent.parent.parent


@router.get("/manifest.json")
async def manifest() -> FileResponse:
    """
    Asynchronously serves the manifest.json file from the static directory.

    Returns:
        FileResponse: A response object that sends the 'static/manifest.json' file to the client.
    """
    manifest_path = BASE_DIR / "static" / "manifest.json"
    return FileResponse(str(manifest_path))
