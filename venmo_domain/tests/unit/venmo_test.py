from unittest import TestCase
from venmo_domain.ports import AccountingResource, SocialResource
from venmo_domain.app.ports import UserResource
from venmo_domain.domain import get_accounting
from venmo_domain.app import MiniVenmo
from venmo_domain.tests.unit.accounting_resource import DictAccountingResource
from venmo_domain.tests.unit.social_resource import DictSocialResource
from venmo_domain.tests.unit.user_resource import DictUserResource
import inject


class VenmoTest(TestCase):
    def setUp(self):
        self.user_resource = DictUserResource()
        self.account_resource = DictAccountingResource()
        self.social_resource = DictSocialResource()
        inject.configure(
            lambda binder: binder.bind(UserResource, self.user_resource)
            .bind(AccountingResource, self.account_resource)
            .bind(SocialResource, self.social_resource),
            clear=True,
        )
        self.accounting = get_accounting()
        self.venmo = MiniVenmo()

    def test_feed_initial(self):
        bobby = self.venmo.create_user('Bobby', 5.00, '4111111111111111')
        feed = bobby.retrieve_feed()
        rendered = self.venmo.render_feed(feed)

        self.assertEqual(
            rendered, 'Bobby received from initial $5.00 for Initial Amount'
        )

    def test_feed_payment(self):
        bobby = self.venmo.create_user('Bobby', 5.00, '4111111111111111')
        carol = self.venmo.create_user('Carol', 10.00, '4242424242424242')

        bobby.pay(carol, 5.00, 'Coffee')

        feed = bobby.retrieve_feed()
        rendered = self.venmo.render_feed(feed)

        self.assertEqual(
            rendered,
            (
                'Bobby received from initial $5.00 for Initial Amount\n'
                'Bobby paid Carol $5.00 for Coffee'
            ),
        )

    def test_feed_reveiced_back(self):
        bobby = self.venmo.create_user('Bobby', 5.00, '4111111111111111')
        carol = self.venmo.create_user('Carol', 10.00, '4242424242424242')

        bobby.pay(carol, 5.00, 'Coffee')
        carol.pay(bobby, 15.00, 'Lunch')

        feed = bobby.retrieve_feed()
        rendered = self.venmo.render_feed(feed)

        self.assertEqual(
            rendered,
            (
                'Bobby received from initial $5.00 for Initial Amount\n'
                'Bobby paid Carol $5.00 for Coffee\n'
                'Bobby received from Carol $15.00 for Lunch'
            ),
        )

    def test_feed_adds_friend(self):
        bobby = self.venmo.create_user('Bobby', 5.00, '4111111111111111')
        carol = self.venmo.create_user('Carol', 10.00, '4242424242424242')

        bobby.pay(carol, 5.00, 'Coffee')
        carol.pay(bobby, 15.00, 'Lunch')
        bobby.add_friend(carol)

        feed = bobby.retrieve_feed()
        rendered = self.venmo.render_feed(feed)

        self.assertEqual(
            rendered,
            (
                'Bobby received from initial $5.00 for Initial Amount\n'
                'Bobby paid Carol $5.00 for Coffee\n'
                'Bobby received from Carol $15.00 for Lunch\n'
                'Bobby adds Carol as friend'
            ),
        )

    def test_run(self):
        MiniVenmo.run()
