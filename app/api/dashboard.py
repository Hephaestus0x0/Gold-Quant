from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/data")
async def dashboard_data():
    return {
        "active_signals": 0,
        "today_signals": 0,
        "win_rate": 0,
        "total_pnl_pips": 0,
        "uptime": "0h",
        "database": "ok",
        "last_data": None,
        "scheduler": "running",
        "recent_signals": [],
        "strategies": [],
        "backtest_results": [],
        "scheduler_jobs": []
    }
