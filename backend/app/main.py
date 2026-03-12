import mimetypes
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.api.router import router
from app.api.oidc.router import oidc_router

app = FastAPI(title="Portal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(oidc_router)

static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():

    @app.middleware("http")
    async def spa_middleware(request: Request, call_next):
        response = await call_next(request)
        path = request.url.path
        # If an API/OIDC route handled it, return as-is
        if response.status_code != 404:
            return response
        # Serve static file if it exists (with correct MIME type)
        file_path = static_dir / path.lstrip("/")
        if file_path.is_file():
            media_type = mimetypes.guess_type(str(file_path))[0]
            return FileResponse(file_path, media_type=media_type)
        # SPA fallback
        return FileResponse(static_dir / "index.html", media_type="text/html")
