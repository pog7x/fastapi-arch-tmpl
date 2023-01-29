from typing import List, Optional

from app.schemas.coffee import CoffeeModel
from app.schemas.user import UserModel


class UserWithCoffeeModel(UserModel):
    coffee: Optional[CoffeeModel] = None


class CoffeeWithUsersModel(CoffeeModel):
    users: Optional[List[UserModel]] = None
