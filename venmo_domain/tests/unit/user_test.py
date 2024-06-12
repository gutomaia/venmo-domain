from unittest import TestCase
from venmo_domain.tests.user_spec import UserSpec
from venmo_domain.domain import User


class UserTest(UserSpec, TestCase):
    def setUp(self):
        self.error = None
        self.user = None

    def given_valid_user(self):
        self.user = User(username='Valid')

    def when_create_user_with(self, **kwargs):
        try:
            self.user = User(**kwargs)
        except Exception as e:
            self.error = e

    def when_add_credit_card(self, credit_card_number):
        try:
            self.user.add_credit_card(credit_card_number)
        except Exception as e:
            self.error = e

    def assert_user_created(self):
        self.assertIsNotNone(self.user)
        self.assertIsNone(self.error)

    def assert_user_not_created(self):
        self.assertIsNone(self.user)
        self.assertIsNotNone(self.error)

    def assert_credit_is_set(self):
        self.assertIsNotNone(self.user)
        self.assertIsNotNone(self.user.credit_card_number)

    def assert_credit_is_not_set(self):
        self.assertIsNotNone(self.user)
        self.assertIsNone(self.user.credit_card_number)

    def assert_error_message(self, field, msg):
        self.assertIsNotNone(self.error)
        errors = self.error.errors()
        error = errors[0]
        location = error['loc'][0]
        self.assertEqual(location, field)
        self.assertEqual(error['msg'], msg)

    def assert_user_has(self, **kwargs):
        self.assertIsNotNone(self.user)
        for k, v in kwargs.items():
            self.assertEqual(v, getattr(self.user, k))
