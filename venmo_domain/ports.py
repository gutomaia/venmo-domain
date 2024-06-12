from abc import abstractmethod, ABCMeta
from decimal import Decimal
from typing import List, Optional
from venmo_domain.types import Username
from datetime import datetime
from pydantic import BaseModel

__all__ = ['AccountingTransaction', 'AccountingResource', 'SocialResource']


class Timeline(BaseModel):
    date: datetime
    username: Username


class StatementLine(Timeline):
    action: str
    target: str
    amount: Decimal
    note: Optional[str] = None


class Friendship(Timeline):
    action: str
    friend: Username


class AccountingTransaction(metaclass=ABCMeta):
    @abstractmethod
    def start_transaction(self):
        """
        Starts transaction
        """

    @abstractmethod
    def commit_transaction(self):
        """
        Commits started transaction
        """

    @abstractmethod
    def rollback_transaction(self, exc_type, exc_value):
        """
        Rollback actual transaction
        """

    @abstractmethod
    def closes_transaction(self):
        """
        Closes and clean up current transaction
        """

    def __enter__(self):
        self.start_transaction()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.commit_transaction()
        else:
            self.rollback_transaction(exc_type, exc_value)
        self.closes_transaction()


class AccountingResource(metaclass=ABCMeta):
    @abstractmethod
    def create_account(
        self, account: str, initial=0, can_be_negative=True
    ) -> None:
        pass

    @abstractmethod
    def account_can_be_negative(self, account) -> bool:
        pass

    @abstractmethod
    def entry(
        self, _from: str, _to: str, amount: Decimal, note: str = None
    ) -> None:
        pass

    @abstractmethod
    def credit_sum(self, account: str) -> Decimal:
        pass

    @abstractmethod
    def debt_sum(self, account: str) -> Decimal:
        pass

    @abstractmethod
    def transaction(self) -> AccountingTransaction:
        pass

    @abstractmethod
    def statements(self) -> List[StatementLine]:
        pass


class SocialResource(metaclass=ABCMeta):
    @abstractmethod
    def timeline(self, username) -> List[Timeline]:
        pass

    @abstractmethod
    def add_friend(self, username, friend):
        pass

    @abstractmethod
    def remove_friend(self, username, friend):
        pass
