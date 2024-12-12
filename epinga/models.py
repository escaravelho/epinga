from datetime import datetime, timedelta
from typing import Annotated, Optional

from sqlmodel import Field, Relationship, SQLModel


class Plan(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    password: str = Field(index=False)
    plan_id: int = Field(foreign_key="plan.id", default=1)
    plan: Plan = Relationship()
    api_keys: Optional[list["APIKey"]] = Relationship(back_populates="user")


class APIKey(SQLModel, table=True):
    id: int = Field(primary_key=True)
    key: str
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="api_keys")
    # Defult to one month from now
    expiration_date: datetime = Field(
        default_factory=lambda: datetime.now() + timedelta(days=30)
    )
