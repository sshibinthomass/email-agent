from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="Service health check")
def health_check():
    return {"status": "healthy", "service": "email-classifier-api"}
