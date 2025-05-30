from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns:
        dict: A dictionary indicating the service status.
    """
    return {"status": "ok"}
