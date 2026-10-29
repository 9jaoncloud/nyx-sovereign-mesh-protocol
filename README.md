# 🌌 Nyx Sovereign Mesh Protocol (NSMP)
### A Zero-GC, Cryptographic Identity-Addressed, Multi-Bearer Ad-Hoc Communication Architecture
**Created by Simeon Bala & 9jaonCloud Engineering**

[![Academic Research Paper](https://img.shields.io/badge/Academic_Paper-Published_Oct_2026-8b5cf6?style=for-the-badge&logo=read-the-docs)](https://nyx.9jaoncloud.com.ng/docs/paper/nyx_sovereign_mesh_protocol_nsmp_2026.html)
[![Download Word DOCX](https://img.shields.io/badge/ResearchGate_DOCX-Download_Paper-2563eb?style=for-the-badge&logo=microsoft-word)](https://nyx.9jaoncloud.com.ng/docs/paper/nyx_sovereign_mesh_protocol_nsmp_2026.docx)
[![Live Research Portal](https://img.shields.io/badge/Live_Portal-nyx.9jaoncloud.com.ng-38bdf8?style=for-the-badge&logo=firefox)](https://nyx.9jaoncloud.com.ng/docs/paper/papers.html)
[![Silicon Verification](https://img.shields.io/badge/Hardware_Verified-Intel_i7--6700HQ-10b981?style=for-the-badge&logo=intel)](https://nyx.9jaoncloud.com.ng/benchmarks.html)
[![License: BSL 1.1 / Reciprocal](https://img.shields.io/badge/License-BSL_1.1_%2F_Reciprocal-f59e0b?style=for-the-badge)](LICENSE.md)

---

## ⚡ Executive Overview

Modern global telecommunications rest on architectural assumptions engineered over forty years ago: centralized naming registries (DNS/ICANN), unauthenticated inter-domain routing protocols (BGP), corporate certificate authority cartels (Web PKI), and the fundamental conflation of endpoint identity with physical topological location in IPv4 and IPv6.

The **Nyx Sovereign Mesh Protocol (NSMP)** is a native next-generation communication and routing protocol engineered to establish resilient, un-censorable, and jitter-free communication across any physical medium.

```
                       [ 1. Complete Sovereignty ]
                       (No DNS, No BGP, No CAs)
                              /         \
                             /           \
                            /             \
                  (Reticulum / Nostr)    (NSMP: Nyx Sovereign Mesh)
                          /                 \
                         /                   \
[ 2. Zero-GC Determinism ] ----------------- [ 3. Multi-Bearer Line-Rate ]
    (Sub-microsecond line rate)  (TCP/IP / QUIC)  (LoRa to 10Gbps Ethernet)
```

---

## 🛡️ The 4 Core Architectural Pillars

1. **Zero-GC Regional Frame Memory**: Packet processing operates within thread-local bump memory arenas, eliminating dynamic heap allocations and stop-the-world Garbage Collection pauses entirely.
2. **Cryptographic Identity Addressing**: Endpoints are identified by a 128-bit Public Key Hash (PKH) represented as dual 64-bit integer registers, enabling single-cycle SIMD identity matching without external IP address registries.
3. **Multi-Bearer Convergence**: A single immutable 44-byte binary frame format bridges seamlessly across long-range sub-GHz LoRa radio (SX1262/SX1276), internet UDP overlays, raw Layer-2 Ethernet, and Bluetooth LE.
4. **Self-Healing Opportunistic Gradient Routing**: Built-in reverse-path learning, a hardware-efficient bitwise anti-replay ring buffer, and deterministic hop-cost metrics that re-route around node failures in milliseconds.

---

## 📊 Hardware-Verified Empirical Benchmarks

All metrics measured directly on physical silicon (**Intel Core i7-6700HQ @ 2.60 GHz, 16 GB DDR4 RAM, Windows 10 x64**):

```text
================================================================
⚡ [NYX SOVEREIGN MESH PROTOCOL: EMPIRICAL MICROBENCHMARK]
Hardware: Intel Core i7-6700HQ @ 2.60GHz | Memory: 16 GB DDR4
Target  : Native Zero-GC Region Machine Code (Pure Silicon Execution)
================================================================

1. Benchmarking NSMP Frame Serialization (N = 100,000)...
   • Total Elapsed Time : 558.655 ms
   • Serialization Rate : 179,001 packets/sec
   • Latency / Packet   : 5,586.55 ns (5.59 µs)

2. Benchmarking NSMP Frame Deserialization (N = 100,000)...
   • Total Elapsed Time : 556.628 ms
   • Deserialization Rate : 179,653 packets/sec
   • Latency / Packet   : 5,566.28 ns (5.57 µs)

3. Benchmarking Router Ingress & Multi-Hop Forwarding (N = 100,000)...
   • Total Elapsed Time : 4.651 ms
   • Forwarding Rate    : 21,500,752 packets/sec (21.50 Mpps)
   • Latency / Packet   : 46.51 ns (0.0465 µs)
   • Verified Forwards  : 100,000

================================================================
✔ PROVABLE HARDWARE EVIDENCE RECORDED (ZERO SYNTHETIC/MOCK NUMBERS).
================================================================
```

---

## 📐 Binary Wire Protocol Specification

Every NSMP frame begins with an immutable 50-byte packed header followed by up to 1,400 bytes of payload:

```text
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|   Magic 'N'   |   Magic 'X'   |    Version    |  Packet Type  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     Flags     |   Hop Limit   |   Hop Count   |   Reserved    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                  Source Address High (64 bits)                |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                  Source Address Low (64 bits)                 |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                Destination Address High (64 bits)             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                Destination Address Low (64 bits)              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Sequence Number (32 bits)                  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|      Payload Length (16 bits) |     Checksum (CRC32, 32 bits) |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Checksum cont.|          Payload Data (0 - 1400 bytes)...    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### Packet Types
- `0x00`: **Announce** &mdash; Cryptographic identity beacon & presence discovery
- `0x01`: **Data** &mdash; End-to-end payload frame
- `0x02`: **Ack** &mdash; Hop-by-hop or end-to-end receipt acknowledgement
- `0x03`: **RouteRequest** &mdash; Reactive path exploration probe
- `0x04`: **RouteReply** &mdash; Path discovery response
- `0x05`: **Telemetry** &mdash; Link quality, SNR, battery, and neighbor report
- `0x06`: **KeepAlive** &mdash; Bearer liveness ping

---

## 🚀 Quickstart & Testing

Run the cross-platform multi-node simulation test:

```bash
# Clone the repository
git clone https://github.com/9jaoncloud/nyx-sovereign-mesh-protocol.git
cd nyx-sovereign-mesh-protocol

# Run Python 3-node simulation (Alice -> Relay -> Bob)
python examples/simulated_mesh_test.py
```

### Compiling the C Reference Example
```bash
gcc -O3 examples/nsmp_packet_example.c -o nsmp_example
./nsmp_example
```

---

## 🧪 Real-World Hardware Testing

See [`TESTING_GUIDE.md`](TESTING_GUIDE.md) for instructions on flashing and testing NSMP across:
1. **Localhost Virtual Sockets** (Impairment simulation with packet loss & jitter).
2. **LilyGO T-Beam & Heltec LoRa 32** (Sub-GHz off-grid radio mesh over SX1262).
3. **Hybrid Gateway Tunnels** (Bridging LoRa radio packets across internet UDP overlays).

---

## ⚖️ License, Attribution & Governance

Copyright &copy; 2026 Simeon Bala & 9jaonCloud Engineering.

This project is licensed under the **Business Source License 1.1 (BSL 1.1)** with a **Reciprocal Community Grant**:
- **Free for Community, Educational & Off-Grid Mesh Use**: Completely free to inspect, deploy, and operate for non-commercial and community mesh networks.
- **Attribution Invariant**: All derivatives and compatible implementations must preserve the Genesis Protocol Attribution to **Simeon Bala & 9jaonCloud Engineering**.
- **Commercial Hardware & OEM Deployment**: Commercial hardware manufacturers, commercial satellite operators, and proprietary drone/avionics integration require a commercial OEM license. See [`LICENSE.md`](LICENSE.md) for details.
- **Official Inquiries & Licensing:** `info@9jaoncloud.com.ng`
