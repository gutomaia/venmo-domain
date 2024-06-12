from decimal import Decimal
from datetime import datetime
from typing import List
from venmo_domain.ports import (
    AccountingResource,
    AccountingTransaction,
    StatementLine,
)
from venmo_domain.errors import WalletNotEnoghtFound
from sqlalchemy import (
    Column,
    Numeric,
    String,
    DateTime,
    Integer,
    Boolean,
    create_engine,
    select,
    or_,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker, declarative_base


class DictAccountingTransaction(AccountingTransaction):
    def start_transaction(self):
        pass

    def commit_transaction(self):
        pass

    def rollback_transaction(self, exc_type, exc_value):
        pass

    def closes_transaction(self):
        pass


class DictAccountingResource(AccountingResource):
    def __init__(self) -> None:
        self.accounts = {}
        self.transactions = []
        self.default_initial_account = 'initial'
        self.check_account_exists = True

    def create_account(
        self, account, initial=Decimal(0), can_be_negative=True
    ) -> None:
        self.accounts[account] = dict(can_be_negative=can_be_negative)
        if initial != Decimal(0):
            self.transactions.append(
                (
                    datetime.now(),
                    self.default_initial_account,
                    account,
                    initial,
                    'Initial Amount',
                )
            )

    def account_can_be_negative(self, account) -> bool:
        if account in self.accounts:
            account = self.accounts[account]
        else:
            for a in self.accounts:
                if a.startswith(account):
                    account = a
                    break
            else:
                account = dict(can_be_negative=True)
        return account['can_be_negative']

    def entry(self, _from, _to, amount: Decimal, note=None) -> None:
        self.transactions.append((datetime.now(), _from, _to, amount, note))

    def debt_sum(self, account):
        return sum(
            [
                debt
                for (_, a, b, debt, _) in self.transactions
                if a.startswith(account)
            ]
        )

    def credit_sum(self, account):
        return sum(
            [
                creds
                for (_, a, b, creds, _) in self.transactions
                if b.startswith(account)
            ]
        )

    def transaction(self) -> AccountingTransaction:
        return DictAccountingTransaction()

    def get_account_str(self, account):
        if account.startswith('/account/'):
            return account[9:]
        return account

    def statements(self, account) -> List[StatementLine]:
        movements = []
        for (date, a, b, amount, note) in self.transactions:
            if a.startswith(account):
                username = self.get_account_str(a)
                target = self.get_account_str(b)
                m = StatementLine(
                    date=date,
                    username=username,
                    action='pays',
                    target=target,
                    amount=amount,
                    note=note,
                )
                movements.append(m)
            elif b.startswith(account):
                username = self.get_account_str(b)
                target = self.get_account_str(a)
                m = StatementLine(
                    date=date,
                    username=username,
                    action='receives',
                    target=target,
                    amount=amount,
                    note=note,
                )
                movements.append(m)
        return movements


Base = declarative_base()


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    can_be_negative = Column(Boolean)


class Entry(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False, default=datetime.now)
    origin = Column(String(80), nullable=False)
    dest = Column(String(80), nullable=False)
    amount = Column(Numeric, nullable=False)
    note = Column(String(200))


class SQLAlchemyTransaction(AccountingTransaction):
    def start_transaction(self):
        pass

    def commit_transaction(self):
        pass

    def rollback_transaction(self, exc_type, exc_value):
        pass

    def closes_transaction(self):
        pass


class SQLAlchemyAccountingResource(AccountingResource):
    def __init__(self) -> None:
        self.default_initial_account = 'initial'
        self.check_account_exists = True
        engine = create_engine('sqlite:///:memory:', echo=True)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def create_account(
        self, account, initial=Decimal(0), can_be_negative=True
    ) -> None:
        a = Account(name=account, can_be_negative=can_be_negative)
        self.session.add(a)
        if initial != Decimal(0):
            e = Entry(
                origin=self.default_initial_account,
                dest=account,
                amount=initial,
                note='Initial Value',
            )
            self.session.add(e)
        self.session.flush()

    def account_can_be_negative(self, account) -> bool:
        query = select(Account).where(Account.name.like(account))
        account = self.session.execute(query).first()
        if account:
            return account[0].can_be_negative
        return True

    def entry(self, _from, _to, amount, note=None) -> None:
        e = Entry(origin=_from, dest=_to, amount=amount, note=note)
        self.session.add(e)
        self.session.flush()

    def debt_sum(self, account):
        query = select(func.sum(Entry.amount)).where(
            Entry.origin.like(account)
        )
        value = self.session.execute(query).scalar()
        return value if value else Decimal(0)

    def credit_sum(self, account):
        query = select(func.sum(Entry.amount)).where(Entry.dest.like(account))
        value = self.session.execute(query).scalar()
        return value if value else Decimal(0)

    def transaction(self) -> AccountingTransaction:
        return SQLAlchemyTransaction()

    def get_account_str(self, account):
        if account.startswith('/account/'):
            return account[9:]
        return account

    def statements(self, account):
        query = select(Entry).where(
            or_(Entry.origin.like(account), Entry.dest.like(account))
        )
        results = self.session.execute(query).all()
        movements = []
        for row in results:
            entry = row[0]
            if entry.origin.startswith(account):
                username = self.get_account_str(entry.origin)
                target = self.get_account_str(entry.dest)
                m = StatementLine(
                    date=entry.date,
                    username=username,
                    action='pays',
                    target=target,
                    amount=entry.amount,
                    note=entry.note,
                )
                movements.append(m)
            elif entry.dest.startswith(account):
                username = self.get_account_str(entry.dest)
                target = self.get_account_str(entry.origin)
                m = StatementLine(
                    date=entry.date,
                    username=username,
                    action='receives',
                    target=target,
                    amount=entry.amount,
                    note=entry.note,
                )
                movements.append(m)

        return movements
