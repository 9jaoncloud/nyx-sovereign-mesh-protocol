# NSMP Verification & Field Testing Guide (RFC-001)

This comprehensive guide details the formal four-tier test methodology for verifying implementations of the **Nyx Sovereign Mesh Protocol (NSMP)** across synthetic simulation, chaotic networks, embedded hardware, and outdoor physical field tests.

---

## Testing Matrix Overview

| Tier | Environment | Scope | Success Criteria |
| :--- | :--- | :--- | :--- |
| **Tier 1** | Memory & Process Simulation | Wire serialization, routing logic, anti-replay | 100% loop termination, zero double delivery, CRC32 match |
| **Tier 2** | Synthetic Chaos Injection | 10%–50% packet drop, jitter, node disconnection | Self-healing discovery, routing table convergence < 2s |
| **Tier 3** | Dual Embedded Hardware Bench | 2x Heltec ESP32 / SX1262 LoRa modules | Over-the-air packet delivery, RSSI/SNR telemetry recording |
| **Tier 4** | Long-Range Line-of-Sight (LoS) | Multi-kilometer field test | 0% packet loss at < -115 dBm, battery life profile |

---

## Tier 1: Standalone Simulation Test

Before flashing embedded silicon, verify packet framing and duplicate filtering locally.

### Execution
Run the reference multi-hop simulation in Python:
```bash
python examples/simulated_mesh_test.py
```

### Expected Output
```text
======================================================================
Nyx Sovereign Mesh Protocol (NSMP) Reference Simulation
======================================================================
Topology Configured:
  Alice: aaaa0000000000011111111111111111
  Relay: bbbb0000000000022222222222222222
  Bob:   cccc0000000000033333333333333333
----------------------------------------------------------------------
[Alice] Transmitting 50-byte wire frame (Total 102 bytes) to Relay...
[Relay] FLOODING: Forwarding to all peers except Alice
[Bob] >>> DELIVERED: 'Sovereign packet payload via zero-GC NSMP mesh wire.' from 1111111111111111 via Relay (Hops: 2)

[Simulating Replay Attack]: Alice's identical packet is re-broadcast by an adversary...
[Relay] DUPLICATE DETECTED: Discarding seq #1001 from 1111111111111111
----------------------------------------------------------------------
[SUCCESS] Multi-hop transmission delivered exactly once. Anti-replay verified.
```

---

## Tier 2: Chaos & Fault-Tolerance Testing

Simulate adversarial link conditions using standard socket impairment or software bridges:

1. **Packet Dropping**: Artificially drop every 3rd packet to test opportunistic retry and multi-path rerouting.
2. **Replay Injection**: Flood previously recorded valid packets into intermediate nodes. The protocol's direct-mapped ring buffer must discard 100% of replays in $O(1)$ time without traversing routing tables.
3. **Partition & Healing**: Disconnect intermediate Relay node. Transmit packets to trigger alternate route requests (`PKT_ROUTE_REQ`). Verify route repair upon link re-establishment.

---

## Tier 3: Dual Embedded Hardware Bench (ESP32 + SX1262)

### Required Bill of Materials
- 2x or 3x ESP32 LoRa development boards (e.g., Heltec Wireless Stick Lite V3, LilyGO T-Beam SX1262).
- Micro-USB / USB-C cables.
- Sub-GHz omnidirectional whip antennas (868 MHz or 915 MHz depending on regional ISM regulation).

### Wiring & Radio Parameters
| Parameter | Setting |
| :--- | :--- |
| **Frequency** | 868.1 MHz (EU) / 915.0 MHz (US) |
| **Bandwidth (BW)** | 125 kHz or 250 kHz |
| **Spreading Factor (SF)** | SF7 (Fast) to SF10 (Long-Range) |
| **Coding Rate (CR)** | 4/5 |
| **Tx Power** | +14 dBm to +22 dBm |

### Verification Steps
1. Flash firmware with NSMP header framing and packet parser.
2. Monitor UART serial consoles at 115200 baud on both devices.
3. Confirm `PKT_ANNOUNCE` beacons received over radio frequency within 5 seconds of boot.
4. Issue a unicast text payload from Node 1 to Node 2. Verify CRC32 match and display received RSSI (e.g., -65 dBm) and SNR (e.g., +9.5 dB).

---

## Tier 4: Long-Range Outdoor Field Testing

Conduct line-of-sight (LoS) and urban obstructed field trials:
1. Place **Base Station (Bob)** at elevated window or mast.
2. Transport **Mobile Node (Alice)** outward at 500m increments: 500m, 1km, 2.5km, 5km.
3. Transmit 100-packet bursts at each waypoint.
4. Record Packet Delivery Ratio (PDR = $\frac{\text{Received}}{\text{Sent}} \times 100\%$) and link margins.
5. In dead zones, position **Relay Node** between Alice and Bob to demonstrate automatic multi-hop bridge restoration.
