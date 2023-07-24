# EVPN Load Generator

This repository contains experimental code that can be used to generate traffic in the EVPN control plane.
To achieve this, we generate Ethernet frames with forged mac addresses which trigger FRR to send BGP update messages.
This way, we can simulate a relatively large number of clients using reasonable hardware requirements.

For reference, we used a 32-Core VM and 32 GB of RAM to simulate 200,000 clients roaming between VTEPs every 25s on average.

## How it works

There are two components as part of the load generator system:

- VTEPs act as endpoints for the overlay networks that participate in the BGP communication.
  - Each VTEP is responsible for a specified range of VNIs.
  - Having too many clients/VNIs on one VTEP can overload it.
- The orchestrator coordinates the VTEPs and simulates the movements of the clients among the VTEPs.
  - When clients roam, they roam to a random VTEP they are currently not connected to.
  - The orchestrator automatically detects available VTEPs for each VNI.

The orchestrator requests the VTEPs to generate a packet originating from a specified MAC address whenever a client roams.

All components are Docker containers so they can be scaled to whatever size needed.

## How to Use

Before starting the load simulation, there are a few things that must be configured.

First off, you need to provide the correct configuration for your VTEPs.
An FRR configuration file can be found in `vtep/frr/frr.conf`.
In particular, you must replace the BGP Route Reflector's IP address with your own.

Next, you will want to configure the VNI ranges for the VTEPs.
You can take the `docker-compose.yaml` as inspiration.
Please note that there should always be at least two VTEPs for each VNI used.

Then, you want to set the `MIN_VTEP_ID` and `MAX_VTEP_ID` for the orchestrator in the docker compose configuration as well.

Now, you must create the directory for the sockets that are used to communicate between the orchestrator and the VTEPs using `mkdir /tmp/wmsim/`.

All further configuration (i.e., the roaming interval) need to be done in the python code of the orchestrator.

Lastly, you will need to configure docker to disable firewall rules so that the VTEPs can communicate properly with the Route Reflector.
To do this, you will need to modify the file `/etc/docker/daemon.json` and set the following properties there:

```json
{
"iptables": false,
"default-address-pools": [
        { "base": "10.241.0.0/16", "size": 24 }
  ]
}
```

This uses the address space `10.241.0.0/16` and you may need to modify it to match your setup. If you change this IP range, you will also need to change the python code (in `vtep/test.py:33`).
