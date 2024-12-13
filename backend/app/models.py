import uuid

from typing import Optional
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    beverages: list["Beverage"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Properties to receive on beverage creation
class Recommendation(SQLModel):
    pass


# many to many relationship between beverages and tags
class BeverageTags(SQLModel, table=True):
    beverage_id: uuid.UUID = Field(foreign_key="beverage.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)


class TagsBase(SQLModel):
    name: str = Field(max_length=255)


class Tags(TagsBase, table=True):
    id: int = Field(default=None, primary_key=True)
    beverages: list["Beverage"] = Relationship(back_populates="tags", link_model=BeverageTags)


class TagsPublic(TagsBase):
    id: int


class CategoryBase(SQLModel):
    name: str = Field(max_length=255)


class Category(CategoryBase, table=True):
    id: int = Field(default=None, primary_key=True)
    beverages: list["Beverage"] = Relationship(back_populates="category")


class CategoryPublic(CategoryBase):
    id: int


# Shared properties
class BeverageBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    category: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    barcode: str | None = Field(default=None, max_length=255)


# Properties to receive on beverage creation
class BeverageCreate(BeverageBase):
    title: str
    category: str | None = None
    description: str | None = None
    barcode: str | None = None
    category_id: int | None = None
    tags: list[int] | None = None
    pass


# Properties to receive on beverage update
class BeverageUpdate(BeverageBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore
    barcode: str | None = Field(default=None, max_length=255)
    tags: list[int] | None = None


# Database model, database table inferred from class name
class Beverage(BeverageBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="beverages")
    tags: list["Tags"] = Relationship(back_populates="beverages", link_model=BeverageTags)
    category_id: int | None = Field(default=None, foreign_key="category.id")
    category: Optional["Category"] = Relationship(back_populates="beverages")


# Properties to return via API, id is always required
class BeveragePublic(BeverageBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    category: Optional["Category"] = None
    barcode: str | None = None
    tags: list[TagsPublic] | None = None


class BeveragesPublic(SQLModel):
    data: list[BeveragePublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
