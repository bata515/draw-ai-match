from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.compare_images import router as test_router

app = FastAPI(title="Draw AI Match", description="画像類似度採点システム")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API router
app.include_router(test_router, prefix="/api")

# Root route to serve the main page
@app.get("/")
async def read_root():
    return FileResponse("static/index.html")