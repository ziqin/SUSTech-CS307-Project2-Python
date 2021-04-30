from abc import ABC
from typing import List

from dto import User


class UserService(ABC):
    async def remove_user(self, user_id: int):
        raise NotImplementedError

    async def get_all_users(self) -> List[User]:
        raise NotImplementedError

    async def get_user(self, user_id: int) -> User:
        raise NotImplementedError
