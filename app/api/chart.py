from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def chart_page(request: Request):
    return templates.TemplateResponse("chart.html", {"request": request})


@router.get("/candles")
async def get_chart_candles(limit: int = Query(500)):
    return []


@router.get("/signals")
async def get_chart_signals(limit: int = Query(100)):
    return []
