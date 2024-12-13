import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Beverage, BeverageCreate, BeveragePublic, BeveragesPublic, BeverageUpdate, Message

router = APIRouter(prefix="/beverages", tags=["beverages"])


@router.get("/", response_model=BeveragesPublic)
def read_beverages(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve beverages.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Beverage)
        count = session.exec(count_statement).one()
        statement = select(Beverage).offset(skip).limit(limit)
        beverages = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Beverage)
            .where(Beverage.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Beverage)
            .where(Beverage.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        beverages = session.exec(statement).all()

    return BeveragesPublic(data=beverages, count=count)


@router.get("/{id}", response_model=BeveragePublic)
def read_beverage(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get beverage by ID.
    """
    beverage = session.get(Beverage, id)
    if not beverage:
        raise HTTPException(status_code=404, detail="Beverage not found")
    if not current_user.is_superuser and (beverage.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return beverage


@router.post("/", response_model=BeveragePublic)
def create_beverage(
    *, session: SessionDep, current_user: CurrentUser, beverage_in: BeverageCreate
) -> Any:
    """
    Create new beverage.
    """
    beverage = Beverage.model_validate(beverage_in, update={"owner_id": current_user.id})
    session.add(beverage)
    session.commit()
    session.refresh(beverage)
    return beverage


@router.put("/{id}", response_model=BeveragePublic)
def update_beverage(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    beverage_in: BeverageUpdate,
) -> Any:
    """
    Update an beverage.
    """
    beverage = session.get(Beverage, id)
    if not beverage:
        raise HTTPException(status_code=404, detail="Beverage not found")
    if not current_user.is_superuser and (beverage.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = beverage_in.model_dump(exclude_unset=True)
    beverage.sqlmodel_update(update_dict)
    session.add(beverage)
    session.commit()
    session.refresh(beverage)
    return beverage


@router.delete("/{id}")
def delete_beverage(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an beverage.
    """
    beverage = session.get(Beverage, id)
    if not beverage:
        raise HTTPException(status_code=404, detail="Beverage not found")
    if not current_user.is_superuser and (beverage.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(beverage)
    session.commit()
    return Message(message="Beverage deleted successfully")
