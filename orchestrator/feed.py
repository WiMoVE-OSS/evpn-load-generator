from time import sleep
from simClient import Client
import numpy as np
import datetime

class Feed:
    def __init__(self, vnis, connections, num_clients, expScale, normal) -> None:
        self.vnis = vnis
        self.connections = connections
        self.expScale = expScale/num_clients 
        self.clients = [Client((i%100)+21) for i in range(num_clients)]
        self.generator = np.random.default_rng()
        self.normal = normal

    def __del__(self) -> None:
        for conn in self.connections.values():
            conn.close()

    def run(self) -> None:
        took = 0
        rest = 0
        while True:
            if self.normal:
                sleep_time = self.generator.exponential(self.expScale) + rest
                rest = 0
                if sleep_time - took < 0:
                    print(f"Can not keep up: {sleep_time-took}")
                    rest = sleep_time - took
                sleep(max(0, sleep_time - took))
                before = datetime.datetime.now()
            index = self.generator.integers(0, len(self.clients))
            self.clients[index].vtep = (self.clients[index].vtep +1) % len(self.vnis[self.clients[index].vni])
            self.connections[self.vnis[self.clients[index].vni][self.clients[index].vtep]].send({"src": self.clients[index].mac, "vni": self.clients[index].vni})
            if self.normal:
                took = ((datetime.datetime.now() - before) / datetime.timedelta(milliseconds=1)) / 1000000.0