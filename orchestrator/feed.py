from multiprocessing.connection import Client
from queue import Queue
import random
import sys
from message import Message
from collections import defaultdict

ADDRESS = ("10.242.2.3", 8000)

class EtherPacket:
    def __init__(self, src: str, dst: str, vni: int) -> None:
        self.src = src
        self.dst = dst
        self.vni = vni

    def toTuple(self) -> tuple:
        return (self.src, self.dst, self.vni)

    def toDict(self) -> dict:
        return {
            "src": self.src,
            "dst": self.dst,
            "vni": self.vni
        }

    def __str__(self) -> str:
        return f"EtherPacket(src={self.src}, dst={self.dst}, vni={self.vni})"

class Feed:
    vnis = defaultdict(lambda: [])
    queue: Queue = Queue()

    def __init__(self) -> None:
        pass

    def __del__(self) -> None:
        self.conn.send("close")
        self.conn.close()

    def getAddress(self, vtep: str) -> tuple:
        return (f"/tmp/wmsim/{vtep}.sock")

    def send(self, message: Message) -> None:
        self.queue.put(message)

    def run(self) -> None:
        while True:
            message = self.queue.get()

            if message.operation == "DISCONNECT":
                return
            if message.operation == "ROAM":
                # get random entry from vni entry
                vni = message.vni
                available = [x for x in self.vnis[vni] if x != message.vtep]
                if len(available) == 0:
                    print("no available vtep")
                    continue
                message.vtep = random.choice(available)
                conn = Client(self.getAddress(message.vtep))
                packet = EtherPacket(message.mac,"12:34:56:78:90:12", message.vni)
                conn.send(packet.toDict())
            if message.operation == "CONNECT":
                vni = message.vni
                available = self.vnis[vni]
                if len(available) == 0:
                    print("no available vtep")
                    continue
                message.vtep = random.choice(available)
                conn = Client(self.getAddress(message.vtep))
                packet = EtherPacket(message.mac,"12:34:56:78:90:12", message.vni)
                conn.send(packet.toDict())
            if message.operation == "KEEPALIVE":
                conn = Client(self.getAddress(message.vtep))
                packet = EtherPacket(message.mac,"12:34:56:78:90:12", message.vni)
                conn.send(packet.toDict())
