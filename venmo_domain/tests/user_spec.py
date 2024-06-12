from unittest import skip


class UserSpec:
    def given_valid_user(self):
        raise NotImplementedError()

    def when_create_user_with(self, **kwargs):
        raise NotImplementedError()

    def when_add_credit_card(self, credit_card_number):
        raise NotImplementedError()

    def assert_user_created(self):
        raise NotImplementedError()

    def assert_user_not_created(self):
        raise NotImplementedError()

    def assert_user_created_with(self, kwargs):
        raise NotImplementedError()

    def assert_credit_is_set(self):
        raise NotImplementedError()

    def assert_credit_is_not_set(self):
        raise NotImplementedError()

    def assert_error_message(self, field, msg):
        raise NotImplementedError()

    def assert_user_has(self, **kwargs):
        raise NotImplementedError()

    def test_create_user_guto(self):
        self.when_create_user_with(username='guto')

        self.assert_user_created()

    def test_create_user_gustavo(self):
        self.when_create_user_with(username='guto')

        self.assert_user_created()

    def test_create_user_with_three_characters(self):
        self.when_create_user_with(username='joe')

        self.assert_user_not_created()

    def test_create_user_with_three_characters_emits_exception(self):
        self.when_create_user_with(username='mai')

        self.assert_error_message(
            'username',
            'Value error, Username must be between 3 and 20 characters long',
        )

    def test_create_user_with_credit_card_number(self):
        self.when_create_user_with(
            username='Bobby', credit_card_number='4111111111111111'
        )

        self.assert_user_has(
            username='Bobby', credit_card_number='4111111111111111'
        )

    def test_create_user_with_invalid_credit_card_number(self):
        self.when_create_user_with(username='Bobby', credit_card_number='1234')

        self.assert_error_message(
            'credit_card_number', 'Value error, Invalid credit card number.'
        )

    def test_add_credit_card_number(self):
        self.given_valid_user()

        self.when_add_credit_card('4111111111111111')

        self.assert_credit_is_set()

    @skip('TODO')
    def test_add_credit_card_with_invalid_number(self):
        self.given_valid_user()

        self.when_add_credit_card('5111111111111111')

        self.assert_credit_is_not_set()

    @skip('TODO')
    def test_add_invalid_credit_card_error_message(self):
        self.given_valid_user()

        self.when_add_credit_card('5111111111111111')

        self.assert_error_message('credit_card_number', 'wera')

    def test_add_credit_card_twice(self):
        self.given_valid_user()

        self.when_add_credit_card('4111111111111111')
        # self.assert_credit_is_set()

        # self.assert_raises()
        # self.when_add_credit_card('4111111111111111')
