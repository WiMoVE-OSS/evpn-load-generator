import os
from time import sleep
from multiprocessing.connection import Client
from queue import Queue
import random
from message import Message
from collections import defaultdict

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
        min_vtep_id = os.environ.get(("MIN_VTEP_ID"))
        max_vtep_id = os.environ.get(("MAX_VTEP_ID"))
        if min_vtep_id is None or max_vtep_id is None:
            print("Min_vtep_id or Max_vtep_id is not configured!")
            exit(1)
        self.connections = {}
        for i in range(int(min_vtep_id), int(max_vtep_id)):
            while True:
                try:
                    conn = Client(self.getAddress(f"{i}"))
                    break
                except:
                    sleep(1)
            data = conn.recv()
            for j in range(data["min_vni"], data["max_vni"]):
                self.vnis[j] += [i]
            self.connections[i] = conn


    def __del__(self) -> None:
        for conn in self.connections.values():
            conn.close()
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
                packet = EtherPacket(message.mac,"12:34:56:78:90:12", message.vni)
                self.connections[message.vtep].send(packet.toDict())
            if message.operation == "CONNECT":
                vni = message.vni
                available = self.vnis[vni]
                if len(available) == 0:
                    print("no available vtep")
                    continue
                message.vtep = random.choice(available)
                packet = EtherPacket(message.mac,"12:34:56:78:90:12", message.vni)
                self.connections[message.vtep].send(packet.toDict())
            if message.operation == "KEEPALIVE":
                packet = EtherPacket(message.mac,"12:34:56:78:90:12", message.vni)
                self.connections[message.vtep].send(packet.toDict())
