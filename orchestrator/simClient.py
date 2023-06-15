from threading import Thread
import time
import numpy as np
from feed import Feed
from message import Message

class Client:
    isConnected = False;
    def __init__(self, id: str, mac: str, feed: Feed, roamE = 60, connectE = 600, disconnectE = 600, vni = 1):
        self.mac = mac
        self.id = id
        self.vni = vni
        self.vtep = None
        self.feed = feed
        self.roamE = roamE
        self.connectE = connectE
        self.disconnectE = disconnectE
        self.keepaliveRunning = False


    def run(self) -> None:
        while True:
            if not Client.isConnected:
                self.disconnectedLoop()
            else:
                self.connectedLoop()

    def initKeepalive(self) -> None:
        if self.keepaliveRunning:
            return
        keepaliveThread = Thread(target=self.keepaliveLoop)
        keepaliveThread.start()
        self.keepaliveRunning = True

    def keepaliveLoop(self) -> None:
        while True:
            if(Client.isConnected):
                self.keepalive()
            time.sleep(60)


    def disconnectedLoop(self) -> None:
        whenToConnect = np.random.exponential(self.connectE)
        print("Client " + self.id + " will connect in " + str(whenToConnect) + " seconds")
        time.sleep(whenToConnect)
        self.connect()

    def connectedLoop(self) -> None:
        timeUntilDisconnect = np.random.exponential(self.disconnectE)
        print("Client " + self.id + " will disconnect in " + str(timeUntilDisconnect) + " seconds")
        timeAtDisconnect = time.time() + timeUntilDisconnect
        while time.time() < timeAtDisconnect:
            timeUntilRoam  = np.random.exponential(self.roamE)
            print("Client " + self.id + " will roam in " + str(timeUntilRoam) + " seconds")
            timeAtRoam = time.time() + timeUntilRoam
            if (timeAtRoam > timeAtDisconnect):
                break
            time.sleep(timeUntilRoam)
            self.roam()
        self.disconnect()

    def roam(self) -> None:
        print("Client " + self.id + " roaming")
        msg = Message(self, "ROAM")
        self.feed.send(msg)

    def connect(self) -> None:
        self.isConnected = True
        self.initKeepalive()
        msg = Message(self, "CONNECT")
        self.feed.send(msg)
        print("Client " + self.id + " connected")

    def disconnect(self) -> None:
        self.isConnected = False
        self.vtep = None
        print("Client " + self.id + " disconnected")

    def keepalive(self) -> None:
        print("Client " + self.id + " sending keepalive")
        msg = Message(self.mac, "KEEPALIVE")
        self.feed.send(msg)
