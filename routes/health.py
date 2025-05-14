from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz", tags=["Health"])
async def health_check() -> dict:
    return {"status": "ok"}
