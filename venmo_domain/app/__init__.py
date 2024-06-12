from .ports import UserResource
from venmo_domain.errors import PaymentException
from inject import autoparams


class MiniVenmo:
    @autoparams('resource')
    def __init__(self, resource: UserResource):
        self.resource = resource

    def create_user(self, username, balance, credit_card_number):
        return self.resource.create_user(username, balance, credit_card_number)

    def render_feed(self, feed):
        msgs = []
        for event in feed:
            if event.action == 'receives':
                msgs.append(
                    f'{event.username} received from {event.target} ${event.amount:.2f} for {event.note}'
                )
            elif event.action == 'pays':
                msgs.append(
                    f'{event.username} paid {event.target} ${event.amount:.2f} for {event.note}'
                )
            elif event.action == 'add_friend':
                msgs.append(f'{event.username} adds {event.friend} as friend')
        return '\n'.join(msgs)

    @classmethod
    def run(cls):
        venmo = cls()

        bobby = venmo.create_user('Bobby', 5.00, '4111111111111111')
        carol = venmo.create_user('Carol', 10.00, '4242424242424242')

        try:
            # should complete using balance
            bobby.pay(carol, 5.00, 'Coffee')

            # should complete using card
            carol.pay(bobby, 15.00, 'Lunch')
        except PaymentException as e:
            print(e)

        feed = bobby.retrieve_feed()
        venmo.render_feed(feed)

        bobby.add_friend(carol)
