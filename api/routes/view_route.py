import fastapi
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = fastapi.APIRouter()
templates = Jinja2Templates(directory="api/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: fastapi.Request):
    return templates.TemplateResponse(request=request, name="index.html")