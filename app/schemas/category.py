from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)
