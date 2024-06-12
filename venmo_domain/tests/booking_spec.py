class BookingSpec:
    def given_account(self, account):
        raise NotImplementedError()

    def given_account_with_amount(self, account, amount, can_be_negative=True):
        raise NotImplementedError()

    def when_transfer(self, _from_account, _to_account, amount):
        raise NotImplementedError()

    def when_statement(self, account):
        raise NotImplementedError()

    def assert_balance(self, account, amount):
        raise NotImplementedError()

    def assert_statements_length(self, length):
        raise NotImplementedError()

    def assert_statement(self, index, **kwargs):
        raise NotImplementedError()

    def test_account_events_timeline(self):
        self.given_account_with_amount('A', 5_000)
        self.given_account('B')

        self.when_transfer('A', 'B', 1_000)

        self.assert_balance('A', 4_000)
        self.assert_balance('B', 1_000)

    def test_account_negative(self):
        self.given_account_with_amount('A', 1_000)
        self.given_account('B')

        self.when_transfer('A', 'B', 2_000)

        self.assert_balance('A', -1_000)
        self.assert_balance('B', 2_000)

    def test_account_get_be_negative(self):
        self.given_account_with_amount('A', 10_000, can_be_negative=False)
        self.given_account('B')

        with self.assertRaises(Exception):
            self.when_transfer('A', 'B', 20_000)

    def test_account_statements(self):
        self.given_account_with_amount('AccA', 10_000, can_be_negative=False)
        self.given_account_with_amount('AccB', 5_000, can_be_negative=False)
        self.given_account('AccC')

        self.when_transfer('AccA', 'AccC', 2_000)
        self.when_transfer('AccA', 'AccB', 1_000)
        self.when_transfer('AccB', 'AccA', 1_000)

        self.when_statement('AccA')

        self.assert_statements_length(4)
        self.assert_statement(
            0, action='receives', target='initial', amount=10_000
        )
        self.assert_statement(1, action='pays', target='AccC', amount=2_000)
        self.assert_statement(2, action='pays', target='AccB', amount=1_000)
        self.assert_statement(
            3, action='receives', target='AccB', amount=1_000
        )
