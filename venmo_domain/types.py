from venmo_domain.errors import UsernameException, CreditCardException
from pydantic import ValidationInfo
import re


class Username(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value, info: ValidationInfo = None):
        if not isinstance(value, str):
            raise TypeError('Username must be a string')
        if len(value) < 4 or len(value) > 15:
            raise UsernameException(
                'Username must be between 3 and 20 characters long'
            )
        if not re.match('^[A-Za-z0-9_\\-]{4,15}$', value):
            raise UsernameException('Username not valid.')
        return cls(value)


class CreditCardNumber(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value, info: ValidationInfo = None):
        if not isinstance(value, str):
            raise TypeError('CreditCardNumber must be a string')
        if value not in ['4111111111111111', '4242424242424242']:
            raise CreditCardException('Invalid credit card number.')
        return cls(value)


class CreditCardNumberDescriptor:
    def __init__(self, name=None):
        self.name = name
        self._values = {}

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self._values.get(instance, None)

    def __set__(self, instance, value):
        validated_value = CreditCardNumber.validate(value)
        self._values[instance] = validated_value

    def __delete__(self, instance):
        if instance in self._values:
            del self._values[instance]
