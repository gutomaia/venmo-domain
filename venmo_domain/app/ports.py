from abc import ABCMeta, abstractmethod
from venmo_domain.domain import User


class UserResource(metaclass=ABCMeta):
    @abstractmethod
    def create_user(self, username, balance, credit_card_number) -> User:
        pass

    @abstractmethod
    def get_user(self, username) -> User:
        """
        Get's User by Username
        """
