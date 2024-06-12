from decimal import Decimal
from venmo_domain.errors import PaymentException


class UserAction:
    def __init__(self, user):
        self.user = user

    def pays(self, user):
        self.target = user
        return self

    def amount(self, amount):
        self.value = Decimal(str(amount))
        return self

    def due(self, note):
        self.note = note

        self.user.pay(self.target, self.value, self.note)
        return self


class WalletSpec:
    def given_user_with(self, **kwargs):
        raise NotImplementedError()

    def given_user_bobby(
        self,
        username='Bobby',
        balance=5.00,
        credit_card_number='4111111111111111',
    ):
        return self.given_user_with(
            username=username,
            balance=balance,
            credit_card_number=credit_card_number,
        )

    def given_user_carol(
        self,
        username='Carol',
        balance=10.00,
        credit_card_number='4242424242424242',
    ):
        return self.given_user_with(
            username=username,
            balance=balance,
            credit_card_number=credit_card_number,
        )

    def when_user(self, user):
        return UserAction(user)

    def assert_balance(self, user, balance):
        raise NotImplementedError()

    def test_wallet_example(self):
        bobby = self.given_user_bobby(balance=5.00)
        carol = self.given_user_with(balance=10.00)

        self.when_user(bobby).pays(carol).amount(5).due('Coffe')

        self.assert_balance(bobby, 0)
        self.assert_balance(carol, 15)
        self.assert_balance('external', 0)

        self.when_user(carol).pays(bobby).amount(15).due('Lunch')

        self.assert_balance(bobby, 15)
        self.assert_balance(carol, 0)
        self.assert_balance('external', 0)

    def test_wallet_without_funds(self):
        bobby = self.given_user_bobby(balance=0)
        carol = self.given_user_carol(balance=0)

        self.when_user(bobby).pays(carol).amount(5).due('Candy')

        self.assert_balance(bobby, 0)
        self.assert_balance(carol, 5)
        self.assert_balance('external', 5)

    def test_wallet_without_funds_only_withdrawn_the_difference(self):
        bobby = self.given_user_bobby(balance=2)
        carol = self.given_user_carol(balance=0)

        self.when_user(bobby).pays(carol).amount(5).due('Candy')

        self.assert_balance(bobby, 0)
        self.assert_balance(carol, 5)
        self.assert_balance('external', 3)

    def test_wallet_ieee_754(self):
        bobby = self.given_user_bobby(balance=0.1)
        carol = self.given_user_carol(balance=100.3)

        self.when_user(bobby).pays(carol).amount(0.1).due('IEEE')

        self.assert_balance(bobby, 0)
        self.assert_balance(carol, 100.4)

    def test_wallet_without_credit_card(self):
        bobby = self.given_user_with(username='Bobby', balance=0)
        carol = self.given_user_carol(balance=0)

        with self.assertRaises(PaymentException) as e:
            self.when_user(bobby).pays(carol).amount(5).due('Birthday')

        self.assert_balance(bobby, 0)
        self.assert_balance(carol, 0)

    def test_wallet_with_amount_zero(self):
        bobby = self.given_user_bobby(balance=0)
        carol = self.given_user_carol(balance=0)

        with self.assertRaises(PaymentException) as e:
            self.when_user(bobby).pays(carol).amount(0).due('Zero')

        self.assert_balance(bobby, 0)
        self.assert_balance(carol, 0)

    def test_wallet_cant_be_used_to_self_pay(self):
        bobby = self.given_user_bobby(balance=10)

        with self.assertRaises(PaymentException) as e:
            self.when_user(bobby).pays(bobby).amount(10).due('Selfpay')

        self.assert_balance(bobby, 10)
