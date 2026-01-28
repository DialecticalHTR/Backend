from fastapi.routing import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(prefix="/health")


@router.get("/")
async def check_health():
    return HTMLResponse(status_code=200)
