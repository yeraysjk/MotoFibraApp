# backend/routes/pedidos.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

@router.get("/pedidos", response_class=HTMLResponse)
async def pedidos(request: Request):
    return templates.TemplateResponse("pedidos.html", {"request": request})
