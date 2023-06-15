import datetime
from enum import Enum
from simClient import Client

class Operation(Enum):
    CONNECT = 1
    ROAM = 2
    DISCONNECT = 3

class Message:
    def __init__(self, client: Client, opCode: Operation):
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
