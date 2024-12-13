import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Recommendation, BeveragesPublic

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.post("/recipes")
def recommendation_recipes(
    *, session: SessionDep, current_user: CurrentUser, item_in: Recommendation
) -> Any:
    """
    Recommentation recipes per beverages.
    """

    return True

@router.post("/beverages", response_model=BeveragesPublic)
def recommendation_beverages(
    *, session: SessionDep, current_user: CurrentUser, item_in: Recommendation
) -> Any:
    """
    Recommentation beverages per recipes.
    """

    return True
