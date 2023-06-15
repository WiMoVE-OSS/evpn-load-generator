import random
from threading import Thread
from simClient import Client
from feed import Feed

feed = Feed()

threads = []

def generate_mac_addresses(n):
    mac_addresses = []
    while len(mac_addresses) < n:
        # Generate a random MAC address
        mac = [random.randint(0x00, 0xff) for _ in range(6)]

        # Set the second least significant bit to 0 to indicate it's a universally administered address
        mac[0] &= 0xfe

        # Set the least significant bit to 1 to indicate it's a unicast address
        mac[0] |= 0x02

        # Convert the MAC address to a string
        mac_address = ':'.join(['{:02x}'.format(x) for x in mac])

        # Check if the MAC address is not a reserved address
        if not is_reserved(mac_address):
            mac_addresses.append(mac_address)

    return mac_addresses

def is_reserved(mac_address):
    # List of reserved MAC address prefixes
    reserved_prefixes = [
        '01:00:0c',  # Cisco
        '01:00:5e',  # IETF (Multicast)
        '33:33',     # IPv6 Neighbor Discovery
        'ff:ff:ff'   # Broadcast
    ]

    # Check if the MAC address starts with any of the reserved prefixes
    for prefix in reserved_prefixes:
        if mac_address.lower().startswith(prefix):
            return True

    return False

for i in range(1, 10):
  client = Client(f"c{i}", generate_mac_addresses(1)[0], feed, 300, 500, 1000, i % 100)
  thread = Thread(target=client.run)
  threads.append(thread)

feedThread = Thread(target=feed.run)
threads.append(feedThread)

for thread in threads:
    thread.start()
