class UsernameException(ValueError):
    """
    UsernameException, as a type must extends from ValueError.
    Due the fact that it emerges when a miss input is placed.
    """

    pass


class PaymentException(ValueError):
    """
    PaymentException, as a type must extends from ValueError.
    Due the fact that it emerges when a miss input is placed.
    """


class CreditCardException(ValueError):
    pass


class WalletNotEnoghtFound(Exception):
    def __init__(self, required_withdrawal=None, *args: object) -> None:
        super().__init__(*args)
        self.required_withdrawal = required_withdrawal

    pass
