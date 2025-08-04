from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
async def test():
    return {"message": "It is a test endpoint!"}
