from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import Optional
import inject
import uuid
from .types import Username, CreditCardNumber
from .errors import PaymentException, WalletNotEnoghtFound
from .ports import AccountingResource, AccountingTransaction, SocialResource
from decimal import Decimal
from datetime import datetime


class User(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    username: Username
    credit_card_number: Optional[CreditCardNumber] = None

    @field_validator('username')
    def validate_username(cls, value: str, info: ValidationInfo) -> str:
        return Username.validate(value)

    @field_validator('credit_card_number')
    def validate_credit_card_number(
        cls, value: str, info: ValidationInfo
    ) -> str:
        return CreditCardNumber.validate(value)

    def set_credit_card_number(self, value: CreditCardNumber):
        self.credit_card_number = value
        self.validate_model()

    def validate_model(self):
        values = self.dict()
        validated_model = self.__class__(**values)
        self.__dict__.update(validated_model.__dict__)

    @property
    def wallet(self):
        if not hasattr(self, '__wallet'):
            self.__wallet = Wallet(self)
        return self.__wallet

    @property
    def social(self):
        if not hasattr(self, '__social'):
            self.__social = get_social(self)
        return self.__social

    @property
    def balance(self):
        return self.wallet.balance()

    def retrieve_feed(self):
        timeline = self.social.timeline()
        statements = self.wallet.statements()
        feed = timeline + statements
        feed.sort(key=lambda x: x.date)
        return feed

    def add_friend(self, new_friend):
        self.social.add_friend(new_friend)

    def add_credit_card(self, credit_card_number):
        self.credit_card_number = credit_card_number

    def pay(self, target, amount, note):
        self.wallet.pay(target, amount, note)


class Accounting:
    def __init__(self, resource: AccountingResource) -> None:
        self.default_params = dict(can_be_negative=True)
        self.default_initial_account = 'initial'
        self.check_account_exists = True
        self.resource = resource

    def create_account(
        self,
        account: str,
        initial: Decimal = Decimal(0),
        can_be_negative: bool = True,
    ) -> None:
        self.resource.create_account(account, initial, can_be_negative)

    def entry(self, _from, _to, amount, note: str = None) -> None:
        if not self.resource.account_can_be_negative(_from):
            balance = self.balance(_from)
            if balance < amount:
                needs_more = amount - balance
                raise WalletNotEnoghtFound(required_withdrawal=needs_more)
        self.resource.entry(_from, _to, amount, note)

    def balance(self, account) -> Decimal:
        debits = self.resource.debt_sum(account)
        credits = self.resource.credit_sum(account)
        return credits - debits

    def transaction(self) -> AccountingTransaction:
        return self.resource.transaction()

    def statements(self, account):
        return self.resource.statements(account)


@inject.autoparams('resource')
def get_accounting(resource: AccountingResource) -> Accounting:
    return Accounting(resource=resource)


def must_have_credit_card(func):
    def wrapper(self, *args):
        if self.user.credit_card_number is None:
            raise PaymentException(
                'Must have a credit card to make a payment.'
            )
        return func(self, *args)

    return wrapper


class Wallet:
    def __init__(self, user: User) -> None:
        self.accounting = get_accounting()
        self.user = user

    @property
    def account(self):
        return f'/account/{self.user.username}'

    def pay(self, target: User, amount, note):
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        if self.user.username == target.username:
            raise PaymentException('User cannot pay themselves.')
        if amount <= Decimal(0):
            raise PaymentException('Amount must be a non-negative number.')

        _to = f'/account/{target.username}'
        try:
            self.accounting.entry(self.account, _to, amount, note)
        except WalletNotEnoghtFound as wnef:
            with self.accounting.transaction():
                self.credit_card_withdrawal(wnef.required_withdrawal)
                """
                Instead of calling again the same entry call, I could add
                a recursion here.
                """
                self.accounting.entry(self.account, _to, amount, note)

    @must_have_credit_card
    def credit_card_withdrawal(self, amount):
        cc_external_account = (
            f'/external/{self.user.username}/{self.user.credit_card_number}'
        )
        # self._charge_credit_card(self.credit_card_number)
        self.accounting.entry(
            cc_external_account, self.account, amount, 'Auto Credit Card Funds'
        )

    def balance(self) -> Decimal:
        return self.accounting.balance(self.account)

    def statements(self):
        return self.accounting.statements(self.account)


class Social:
    def __init__(self, user: User, resource: SocialResource) -> None:
        self.user = user
        self.resouce = resource

    def add_friend(self, friend: User):
        self.resouce.add_friend(self.user.username, friend.username)

    def timeline(self):
        return self.resouce.timeline(self.user.username)


@inject.autoparams('resource')
def get_social(user, resource: SocialResource) -> Social:
    return Social(user, resource=resource)
