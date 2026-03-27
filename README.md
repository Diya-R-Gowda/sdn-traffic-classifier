# SDN Traffic Classification System

## Problem Statement
Classify network traffic based on protocol type (TCP/UDP/ICMP)
using an SDN controller and OpenFlow rules.

## Objectives
- Identify TCP, UDP, ICMP packets at the controller
- Maintain per-protocol packet/byte statistics
- Display classification results in real time
- Analyze traffic distribution

## Topology
3 hosts (h1, h2, h3) connected to 1 OVS switch, controlled by Ryu

## Setup & Execution
1. Start Ryu controller:
   ryu-manager traffic_classifier.py

2. In a second terminal, start topology:
   sudo python3 topology.py

3. Inside Mininet CLI, run tests:
   pingall                          # ICMP test
   h2 iperf -s &                   # TCP server
   h1 iperf -c 10.0.0.2 -t 10     # TCP client
   h2 iperf -s -u &                # UDP server
   h1 iperf -c 10.0.0.2 -u -b 1M  # UDP client

## Expected Output
Controller terminal shows per-packet classification and a
summary table every 10 packets showing protocol distribution.

## Tools Used
- Mininet, Ryu, Open vSwitch, Wireshark, iperf

## References
- https://mininet.org/overview/
- https://ryu.readthedocs.io/
- https://mininet.org/walkthrough/
