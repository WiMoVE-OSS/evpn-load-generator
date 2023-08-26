from threading import Thread
from multiprocessing.connection import Client
from feed import Feed
from time import sleep
import os
from collections import defaultdict

num_feeds = 10

def getAddress(vtep: str):
    return (f"/tmp/wmsim/{vtep}.sock")

min_vtep_id = os.environ.get(("MIN_VTEP_ID"))
max_vtep_id = os.environ.get(("MAX_VTEP_ID"))
if min_vtep_id is None or max_vtep_id is None:
    print("Min_vtep_id or Max_vtep_id is not configured!")
    exit(1)
connections = {}
vnis = defaultdict(lambda: [])
for i in range(int(min_vtep_id), int(max_vtep_id)):
    print(f"Trying to connect to {i}")
    while True:
        print(getAddress(f"{i}"))
        try:
            conn = Client(getAddress(f"{i}"))
            break
        except Exception as e: 
            print(e)
            print(f"Connect to {i} failed")
            sleep(1)
    data = conn.recv()
    for j in range(data["min_vni"], data["max_vni"]):
        vnis[j] += [i]
    connections[i] = conn
print("Established all connections")

feeds = [Feed(vnis, connections, 40000, 25, True) for i in range(num_feeds)]

threads = []

for j in range(num_feeds):
    feedThread = Thread(target=feeds[j].run)
    feedThread.start()
