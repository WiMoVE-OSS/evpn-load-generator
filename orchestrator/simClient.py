import datetime
import numpy as np
import random

def generate_mac_address():
    # Generate a random MAC address
    mac = [random.randint(0x00, 0xff) for _ in range(6)]

    # Set the second least significant bit to 0 to indicate it's a universally administered address
    mac[0] &= 0xfe

    # Set the least significant bit to 1 to indicate it's a unicast address
    mac[0] |= 0x02

    # Convert the MAC address to a string
    mac_address = ':'.join(['{:02x}'.format(x) for x in mac])

    # Check if the MAC address is not a reserved address

    return mac_address

class Client:
    def __init__(self, vni = 1):
        self.mac = generate_mac_address()
        self.vni = vni
        self.vtep = 0
