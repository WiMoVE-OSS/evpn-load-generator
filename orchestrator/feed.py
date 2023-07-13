from time import sleep
from simClient import Client
import random
import numpy as np
import datetime

class Feed:
    def __init__(self, vnis, connections, num_clients, expScale) -> None:
        self.vnis = vnis
        self.connections = connections
        self.expScale = expScale/num_clients 
        self.clients = [Client((i%100)+21) for i in range(num_clients)]
        self.generator = np.random.default_rng()

    def __del__(self) -> None:
        for conn in self.connections.values():
            conn.close()

    def run(self) -> None:
        took = 0
        while True:
            sleep_time = self.generator.exponential(self.expScale)
            if sleep_time - took < 0:
                print(f"Can not keep up: {sleep_time-took}")
            sleep(max(0, sleep_time - took))
            before = datetime.datetime.now()
            index = self.generator.integers(0, len(self.clients))
            new_vtep = self.clients[index].vtep
            while new_vtep == self.clients[index].vtep:
                new_vtep = random.choice(self.vnis[self.clients[index].vni])
            #print(f"Roam for client {self.clients[index].mac} from {self.clients[index].vtep} to {new_vtep}")
            self.clients[index].vtep = new_vtep
            self.connections[self.clients[index].vtep].send({"src": self.clients[index].mac, "vni": self.clients[index].vni})
            took = ((datetime.datetime.now() - before) / datetime.timedelta(milliseconds=1)) / 1000000.0