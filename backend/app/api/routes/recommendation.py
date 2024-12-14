import uuid
from typing import Any
import json
from fastapi import APIRouter, HTTPException, Request
from sqlmodel import func, select
from app.api.deps import CurrentUser, SessionDep, AIDep
from app.core.open_ai import get_recipes, GET_RECIPES_JSON_SCHEMA
from app.models import Recommendation, BeveragesPublic, Barcode, Beverage, RecommendationResponse
from openai.types.chat import ChatCompletionMessage
router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/recipesByBarcode", response_model=RecommendationResponse, response_model_exclude_none=True)
def recommendation_recipes(barcode: Barcode, session: SessionDep, current_user: CurrentUser, ai_client: AIDep) -> Any:
    """
    Recommendation of cocktails and side dishes by barcode.
    """
    beverage = session.exec(select(Beverage).where(Beverage.barcode == barcode.barcode)).first()
    beverage_description, ai_response = get_recipes(ai_client, beverage)
    recipes = json.loads(ai_response.content)
    cocktails = recipes["cocktails"]
    sideDishes = recipes["sideDishes"]
    beverage = beverage_description
    return {"debugInfo": {"beverage": beverage}, "cocktails": cocktails, "sideDishes": sideDishes}


@router.post("/beveragesByRecipe", response_model=BeveragesPublic)
def recommendation_beverages(
    *, session: SessionDep, current_user: CurrentUser, item_in: Recommendation
) -> Any:
    """
    Recommendation of beverages by recipe.
    """

    return True
