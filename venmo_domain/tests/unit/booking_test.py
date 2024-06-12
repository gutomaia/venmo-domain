from unittest import TestCase
from decimal import Decimal
from venmo_domain.tests.booking_spec import BookingSpec
from venmo_domain.domain import Accounting
from venmo_domain.tests.unit.accounting_resource import (
    DictAccountingResource,
    SQLAlchemyAccountingResource,
)


class BookingTest(BookingSpec, TestCase):
    def setUp(self) -> None:
        resource = DictAccountingResource()
        self.booker = Accounting(resource)

    def given_account(self, account):
        self.booker.create_account(account)

    def given_account_with_amount(self, account, amount, can_be_negative=True):
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        self.booker.create_account(
            account, initial=amount, can_be_negative=can_be_negative
        )

    def when_transfer(self, _from_account, _to_account, amount):
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        self.booker.entry(_from_account, _to_account, amount)

    def when_statement(self, account):
        self.statements = self.booker.statements(account)

    def assert_balance(self, account, amount):
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        funds = self.booker.balance(account)
        self.assertEqual(funds, amount)

    def assert_statements_length(self, length):
        self.assertEqual(len(self.statements), length)

    def assert_statement(self, index, **kwargs):
        statement = self.statements[index]
        for k, v in kwargs.items():
            if k == 'amount':
                if not isinstance(v, Decimal):
                    v = Decimal(str(v))
            self.assertEqual(v, getattr(statement, k))


class SQLAlchemyBookingTest(BookingTest):
    def setUp(self) -> None:
        resource = SQLAlchemyAccountingResource()
        self.booker = Accounting(resource)
