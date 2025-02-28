from .dtos import ResponseUsers
from src.factory.utils import load_users_list

class Users():
    def __init__(self) -> None:
        self.users_list = load_users_list()

    def get(self):
        return ResponseUsers(users=self.users_list)