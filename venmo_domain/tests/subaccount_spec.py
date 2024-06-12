class SubAccountSpec:
    def given_account(self, account):
        raise NotImplementedError()

    def given_account_with_amount(self, account, amount, can_be_negative=True):
        raise NotImplementedError()

    def when_transfer(self, _from_account, _to_account, amount):
        raise NotImplementedError()

    def assert_balance(self, account, amount):
        raise NotImplementedError()

    def test_subaccount_balance(self):
        self.given_account('main:A')

        self.given_account_with_amount('main:A:savings', 100)
        self.given_account_with_amount('main:A:principal', 1000)

        self.assert_balance('main:A', 1100)

    def test_subaccount_transactions_with_negative_transfers(self):
        self.given_account('main:A')

        self.when_transfer('main:A:savings', 'debts:main:A:savings', 100)
        self.when_transfer('main:A:principal', 'debts:main:A:principal', 1000)

        self.assert_balance('debts:main:A', 1100)
        self.assert_balance('main:A', -1100)

    def test_subaccount_with_uneven_balance(self):
        self.given_account('main:A')

        self.when_transfer('main:A:savings', 'Debts:main:A:savings', 100)
        self.when_transfer('main:A:principal', 'Debts:main:A:principal', 1000)
        self.when_transfer('external:client:A', 'main:A:payment', 1100)

        self.assert_balance('main:A', 0)
