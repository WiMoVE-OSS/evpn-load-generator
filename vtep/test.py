#!/usr/bin/env python3
from multiprocessing.connection import Listener
import socket
import os

def send_frame(s, srcmac):

    payload_bytes = "TEST".encode('utf-8')
    assert len(payload_bytes) <= 1500  # Ethernet MTU

    frame = human_mac_to_bytes("56:78:90:12:34:56") + \
            human_mac_to_bytes(srcmac) + \
            b'\x7A\x05' + \
            payload_bytes

    # Send Ethernet frame
    return s.send(frame)

def human_mac_to_bytes(addr):
    return bytes.fromhex(addr.replace(':', ''))

def get_veth_names(n):
    return [f"veth{n}_1", f"veth{n}_2"]

def get_bridge_name(n):
    return f"br{n}"

def get_vxlan_name(n):
    return f"vxlan{n}"

def main():
    # Get IP from docker container
    ip = os.popen("ip a | grep 10.241. | cut -d ' ' -f6 | cut -d '/' -f1").read().split()[0]
    min_vni = os.environ.get("MIN_VNI")
    max_vni = os.environ.get("MAX_VNI")
    vtep_id = os.environ.get("VTEP_ID")
    if min_vni is None or max_vni is None or vtep_id is None:
        print("Environment is not configured properly!")
        exit(1)
    min_vni = int(min_vni)
    max_vni = int(max_vni) +1
    print("IP is: ", ip)
    print("VTEP_ID is: ", vtep_id)
    print("MIN_VNI is: ",min_vni)
    print("MAX_VNI is: ", max_vni)
  
    for i in range(min_vni, max_vni): 
        if i % 100 == 0:
            print(f"Setting up vni: {i}")
        # Create veths
        veth_names = get_veth_names(i)
        os.system(f"ip link add {veth_names[0]} type veth peer name {veth_names[1]}")
        # Create bridge
        os.system(f"ip link add name {get_bridge_name(i)} type bridge")
        # Create VXLAN
        os.system(f"ip link add {get_vxlan_name(i)} type vxlan id {i} dstport 4789 local {ip} nolearning")
        # Add ifaces to bridge
        os.system(f"ip link set {get_vxlan_name(i)} master {get_bridge_name(i)}")
        os.system(f"ip link set {veth_names[1]} master {get_bridge_name(i)}")
        # Set all ifaces up
        os.system(f"ip link set dev {veth_names[0]} up")
        os.system(f"ip link set dev {veth_names[1]} up")

        os.system(f"ip link set {get_bridge_name(i)} up")
        os.system(f"ip link set {get_vxlan_name(i)} up")

    # Generate Sockets
    sockets = {i: socket.socket(socket.AF_PACKET, socket.SOCK_RAW) for i in range(min_vni, max_vni)}
    for key, s in sockets.items():
        # Open raw socket and bind it to network interface.
        s.bind((get_veth_names(key)[0], 0))

    # Get frr ready
    with open('/etc/frr/frr.conf', 'r') as file:
        data = file.read()

    # Replace the target string
    data = data.replace('IP', ip)

    with open('/etc/frr/frr.conf', 'w') as file:
        file.write(data)

    # Start frr
    os.system("/usr/lib/frr/frrinit.sh start")

    with Listener(f"/tmp/wmsim/{vtep_id}.sock") as listener:
        with listener.accept() as conn:
            print('connection accepted from', listener.last_accepted)
            conn.send({"min_vni":min_vni, "max_vni":max_vni, "ip":ip})
            while True:
                data = conn.recv()
                #print(data)
                send_frame(sockets[data["vni"]], data["src"])


if __name__ == "__main__":
    main()
