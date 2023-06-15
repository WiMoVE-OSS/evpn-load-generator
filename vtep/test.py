#!/usr/bin/env python3
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

def get_socket(vni, min_vni, max_vni, sockets):
    if (vni < min_vni):
        return
    if (vni + min_vni > max_vni):
        return
    return sockets[vni-min_vni]



def main():
    # Get IP from docker container
    ip = os.popen("ip a | grep 10.241. | cut -d ' ' -f6 | cut -d '/' -f1").read()
    min_vni = os.environ.get("MIN_VNI")
    max_vni = os.environ.get("MAX_VNI")
    if min_vni is None or max_vni is None:
        print("Min_vni or Max_vni is not configured!")
        exit(1)
  
    for i in range(min_vni, max_vni): 
        # Create veths
        veth_names = get_veth_names(i)
        os.system(f"ip link add {veth_names[0]} peer name {veth_names[1]}")
        # Create bridge
        os.system(f"ip link add name {get_bridge_name(i)} type bridge")
        # Create VXLAN
        os.system(f"ip link add {get_vxlan_name(i)} type vxlan id {i} dstport 4789 local {ip} nolearning")
        # Add ifaces to bridge
        os.system(f"ip link set {get_vxlan_name(i)} master {get_bridge_name(i)}")
        os.system(f"ip link set {veth_names[1]} master {get_bridge_name(i)}")

    # Generate Sockets
    sockets = [socket.socket(socket.AF_PACKET, socket.SOCK_RAW) for _ in range(min_vni, max_vni)]
    for i in range(min_vni, max_vni):
        # Open raw socket and bind it to network interface.
        s = get_socket(i, min_vni, max_vni, sockets)
        s.bind((get_veth_names(i)[0], 0))

    # Get frr ready
    with open('/etc/frr/frr.conf', 'r') as file:
        data = file.read()

    # Replace the target string
    data = data.replace('IP', ip)

    with open('/etc/frr/frr.conf', 'w') as file:
        file.write(data)

    # Start frr
    os.system("/usr/lib/frr/frrinit.sh start")

    for i in range(min_vni, max_vni):
        send_frame(get_socket(i, min_vni, max_vni, sockets), "12:34:56:78:90:12")

    while True:
        pass


if __name__ == "__main__":
    main()
