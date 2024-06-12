from decimal import Decimal


class SocialSpec:
    def given_user_with(self, **kwargs):
        raise NotImplementedError()

    def when_add_friend(self, user, target):
        raise NotImplementedError()

    def when_feed(self, user):
        raise NotImplementedError()

    def assert_has_friend(self, user, target):
        raise NotImplementedError()

    def assert_has_no_friends(self, user):
        raise NotImplementedError()

    def assert_feed(self, *timeline):
        raise NotImplementedError()

    def test_add_friend(self):
        tom = self.given_user_with(username='Tomcat')
        jerry = self.given_user_with(username='Jerry')

        self.when_add_friend(tom, jerry)

        self.assert_has_friend(tom, jerry)

    def test_add_friend_multiple(self):
        superman = self.given_user_with(username='Superman')
        batman = self.given_user_with(username='Batman')
        wonderwoman = self.given_user_with(username='WonderWoman')

        self.when_add_friend(superman, batman)
        self.when_add_friend(superman, wonderwoman)

        self.when_add_friend(wonderwoman, superman)
        self.when_add_friend(wonderwoman, batman)

        self.assert_has_friend(superman, batman)
        self.assert_has_friend(superman, wonderwoman)
        self.assert_has_friend(wonderwoman, superman)
        self.assert_has_friend(wonderwoman, batman)
        self.assert_has_no_friends(batman)

    def test_feed_add_friend(self):
        parker = self.given_user_with(username='peterparker')
        maryj = self.given_user_with(username='maryj')

        self.when_add_friend(parker, maryj)

        self.when_feed(parker)

        self.assert_feed(dict(action='add_friend', friend='maryj'))

    def test_feed_pay_user(self):
        madruga = self.given_user_with(username='madruga')
        barriga = self.given_user_with(username='barriga')

        self.when_pays(madruga, barriga, 1999.99, 'Rent')

        self.when_feed(madruga)
        self.assert_feed(
            dict(
                action='pays',
                target='barriga',
                amount=Decimal('1999.99'),
                note='Rent',
            )
        )

        self.when_feed(barriga)
        self.assert_feed(
            dict(
                action='receives',
                target='madruga',
                amount=Decimal('1999.99'),
                note='Rent',
            )
        )
