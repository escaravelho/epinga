import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Beverage, BeverageCreate, BeveragePublic, BeveragesPublic, BeverageUpdate, Message

router = APIRouter(prefix="/beverages", tags=["beverages"])


@router.get("/", response_model=BeveragesPublic)
def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Beverage)
        count = session.exec(count_statement).one()
        statement = select(Beverage).offset(skip).limit(limit)
        items = session.exec(statement).all()
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
        items = session.exec(statement).all()

    return BeveragesPublic(data=items, count=count)


@router.get("/{id}", response_model=BeveragePublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get item by ID.
    """
    item = session.get(Beverage, id)
    if not item:
        raise HTTPException(status_code=404, detail="Beverage not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item


@router.post("/", response_model=BeveragePublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: BeverageCreate
) -> Any:
    """
    Create new item.
    """
    item = Beverage.model_validate(item_in, update={"owner_id": current_user.id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.put("/{id}", response_model=BeveragePublic)
def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: BeverageUpdate,
) -> Any:
    """
    Update an item.
    """
    item = session.get(Beverage, id)
    if not item:
        raise HTTPException(status_code=404, detail="Beverage not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{id}")
def delete_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    item = session.get(Beverage, id)
    if not item:
        raise HTTPException(status_code=404, detail="Beverage not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(item)
    session.commit()
    return Message(message="Beverage deleted successfully")
