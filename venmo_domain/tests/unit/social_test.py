from unittest import TestCase
from venmo_domain.app.ports import UserResource
from venmo_domain.ports import AccountingResource, SocialResource
from venmo_domain.tests.social_spec import SocialSpec
from venmo_domain.domain import User, get_accounting
from venmo_domain.tests.unit.accounting_resource import DictAccountingResource
from venmo_domain.tests.unit.social_resource import DictSocialResource
import inject


class SocialTest(SocialSpec, TestCase):
    def setUp(self):
        self.social_resource = DictSocialResource()
        self.account_resource = DictAccountingResource()
        inject.configure(
            lambda binder: binder.bind(
                SocialResource,
                self.social_resource,
            ).bind(AccountingResource, self.account_resource),
            clear=True,
        )
        self.accounting = get_accounting()

        self.error = None
        self.user = None

    def given_user_with(self, **kwargs):
        self.user = User(**kwargs)
        return self.user

    def when_add_friend(self, user, target):
        user.add_friend(target)

    def when_feed(self, user):
        self.feed = user.retrieve_feed()

    def when_pays(self, user, target, amount, note):
        user.pay(target, amount, note)

    def assert_has_friend(self, user, friend):
        network = self.social_resource.network
        self.assertIn(user.username, network)
        self.assertIn(friend.username, network[user.username])

    def assert_has_no_friends(self, user):
        if user.username in self.social_resource.network:
            self.assertEqual(
                0, len(self.social_resource.network[user.username])
            )

    def assert_feed(self, *timeline):
        self.assertEqual(len(self.feed), len(timeline))
        for index, post in enumerate(timeline):
            for k, v in post.items():
                self.assertEqual(v, getattr(self.feed[index], k))
