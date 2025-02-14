from fastapi import APIRouter, FastAPI
from fastapi.responses import RedirectResponse

from src.routers import storage

app = FastAPI()


app = FastAPI(
    title="Keeper API",
    description="This API was built to handle key-value storage",
    version="1.0.0",
    docs_url="/api/docs",
)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/api/docs")


router: APIRouter = APIRouter(prefix="/api")

router.include_router(storage.router)

app.include_router(router)
