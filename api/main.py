from fastapi import FastAPI

from api.compare_images import router as test_router

app = FastAPI()

app.include_router(test_router, prefix="/api")