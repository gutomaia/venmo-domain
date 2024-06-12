from unittest import TestCase
from venmo_domain.tests.subaccount_spec import SubAccountSpec
from venmo_domain.domain import Accounting
from venmo_domain.tests.unit.accounting_resource import DictAccountingResource


class SubAccount(SubAccountSpec, TestCase):
    def setUp(self) -> None:
        resource = DictAccountingResource()
        self.booker = Accounting(resource)

    def given_account(self, account):
        self.booker.create_account(account)

    def given_account_with_amount(self, account, amount, can_be_negative=True):
        self.booker.create_account(
            account, initial=amount, can_be_negative=can_be_negative
        )

    def when_transfer(self, _from_account, _to_account, amount):
        self.booker.entry(_from_account, _to_account, amount)

    def assert_balance(self, account, amount):
        funds = self.booker.balance(account)
        self.assertEqual(funds, amount)
