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

## Flow Table from the Mininet Terminal
<img width="1217" height="511" alt="image" src="https://github.com/user-attachments/assets/ccf6c4ff-e2ad-4a50-9cf2-55bb6ce59885" />

## Wireshark Screenshots

## Wireshark ICMP
<img width="1220" height="760" alt="image" src="https://github.com/user-attachments/assets/88dbdb8e-1c1b-4c9d-9976-a77159cb97b4" />

## Wireshark TCP
<img width="1220" height="760" alt="image" src="https://github.com/user-attachments/assets/8bdb7bf3-67f0-4ee7-bca7-2c7321445a56" />

## Wireshark UDP
<img width="1220" height="760" alt="image" src="https://github.com/user-attachments/assets/1ca485e0-7ff8-42e0-93dd-dbf39f88ef49" />

## RYU Controller Logs
<img width="1221" height="658" alt="image" src="https://github.com/user-attachments/assets/28a9ed23-d5e1-4d26-9d0f-926cc08c19d4" />

## pingall result
<img width="1212" height="27" alt="image" src="https://github.com/user-attachments/assets/ef0adc06-28e4-4ec8-81da-292ebf73975d" />
<img width="1221" height="682" alt="image" src="https://github.com/user-attachments/assets/2379fa80-a596-40cf-aa9d-f3cf9b743619" />




