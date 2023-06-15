import datetime
from enum import Enum

class Operation(Enum):
    CONNECT = 1
    ROAM = 2
    DISCONNECT = 3
    KEEPALIVE = 4

class Message:
    def __init__(self, client, opCode: Operation):
        self.mac = client.mac
        self.username = client.id
        self.vni = client.vni
        self.vtep = client.vtep
        self.operation = opCode

    def toDict(self):
        return {
            "mac": self.mac,
            "username": self.username,
            "vni": self.vni,
            "vtep": self.vtep,
            "operation": self.operation.name
        }
