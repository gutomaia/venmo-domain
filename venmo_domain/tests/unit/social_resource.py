from venmo_domain.ports import SocialResource, Friendship
from datetime import datetime


class DictSocialResource(SocialResource):
    def __init__(self) -> None:
        self.network = {}
        self.events = []

    def timeline(self, username) -> Friendship:
        return [
            Friendship(
                date=event['date'],
                username=event['user'],
                action=event['action'],
                friend=event['friend'],
            )
            for event in self.events
            if event['user'] == username
        ]

    def add_friend(self, username, friend):
        added = False
        if username not in self.network:
            self.network[username] = [friend]
            added = True
        elif friend not in self.network[username]:
            self.network[username].append(friend)
            added = True

        if added:
            self.events.append(
                dict(
                    date=datetime.now(),
                    user=username,
                    action='add_friend',
                    friend=friend,
                )
            )

    def remove_friend(self, username, friend):
        if username in self.network:
            if friend in self.network[username]:
                self.network[username].remove(friend)
                self.events.append(
                    dict(
                        date=datetime.now(),
                        user=username,
                        action='remove_friend',
                        args=[friend],
                    )
                )
