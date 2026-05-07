from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter()


@router.post("/input")
async def integration_input(body: dict, db: Session = Depends(get_db)):
    """Log data from external source (e.g., sleep tracker, stress monitor)."""
    return {"status": "logged", "data": body}


@router.get("/output")
async def integration_output(module: str = "", user_id: int = 1, db: Session = Depends(get_db)):
    """Return recommendations for external system."""
    return {"module": module, "recommendations": []}
