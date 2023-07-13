
class Message:
    def __init__(self, client, timestamp):
        self.client = client
        self.timestamp = timestamp

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def __eq__(self, other) -> bool:
        return self.timestamp == other.timestamp