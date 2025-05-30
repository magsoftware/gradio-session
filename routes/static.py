from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/manifest.json")
async def manifest():
    """
    Asynchronously serves the manifest.json file from the static directory.

    Returns:
        FileResponse: A response object that sends the 'static/manifest.json' file to the client.
    """
    return FileResponse("static/manifest.json")
