from fastapi import APIRouter

router = APIRouter()


@router.get("/semantic")
def semantic():
    return {"message": "Semantic"}
