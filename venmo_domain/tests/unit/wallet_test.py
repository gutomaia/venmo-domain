from unittest import TestCase
import inject
from decimal import Decimal
from venmo_domain.ports import AccountingResource
from venmo_domain.tests.unit.accounting_resource import (
    DictAccountingResource,
    SQLAlchemyAccountingResource,
)
from venmo_domain.tests.wallet_spec import WalletSpec
from venmo_domain.domain import User, get_accounting


class WalletTest(WalletSpec, TestCase):
    def setUp(self):
        self.account_resource = DictAccountingResource()
        inject.configure(
            lambda binder: binder.bind(
                AccountingResource, self.account_resource
            ),
            clear=True,
        )
        self.accounting = get_accounting()

    def given_user_with(self, username='Valid', balance=Decimal(0), **kwargs):
        self.user = User(username=username, **kwargs)
        balance = Decimal(str(balance))

        self.account_resource.create_account(
            self.user.wallet.account,
            balance,
            can_be_negative=False,
        )
        return self.user

    def assert_balance(self, object, balance):
        expected = Decimal(str(balance))

        if isinstance(object, User):
            self.assertEqual(object.balance, expected)
        elif isinstance(object, str):
            self.accounting.balance(object)


class SQLAlchemyWalletTest(WalletTest):
    def setUp(self):
        self.account_resource = SQLAlchemyAccountingResource()
        inject.configure(
            lambda binder: binder.bind(
                AccountingResource, self.account_resource
            ),
            clear=True,
        )
        self.accounting = get_accounting()
