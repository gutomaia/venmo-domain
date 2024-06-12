from decimal import Decimal
from venmo_domain.app.ports import UserResource
from venmo_domain.domain import User, get_accounting


class DictUserResource(UserResource):
    def __init__(self) -> None:
        self.users = []

    def create_user(self, username, balance, credit_card_number) -> User:
        user = User(username=username, credit_card_number=credit_card_number)
        balance = Decimal(str(balance))

        get_accounting().create_account(
            user.wallet.account,
            balance,
            can_be_negative=False,
        )
        return user

    def get_user(self, username) -> User:
        return super().get_user(username)
