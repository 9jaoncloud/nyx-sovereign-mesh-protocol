# RFC-001: Nyx Sovereign Mesh Protocol (NSMP) Specification
### Version 1.0 &mdash; Standards Track
**Author:** Simeon Bala & 9jaonCloud Engineering  
**Date:** October 2026  
**Status:** Canonical Reference Specification  

---

## 1. Abstract
This document specifies the wire framing, cryptographic addressing, and routing dynamics of the Nyx Sovereign Mesh Protocol (NSMP). NSMP provides an ad-hoc, multi-bearer network layer operating independently of ICANN, DNS, BGP, and central Certificate Authorities.

---

## 2. Terminology & Addressing Model

### 2.1 Node Identifier (NodeAddress)
Endpoints are identified by a 128-bit cryptographic hash of their public key:

$$\mathcal{I} = \text{Truncate}_{128}\left(\text{BLAKE3}(\text{PubKey})\right) = (H_{\text{hi}}, L_{\text{lo}})$$

- **Representation**: Two 64-bit unsigned integers: `src_hi`, `src_lo`.
- **Special Addresses**:
  - `Broadcast`: `0xFFFFFFFFFFFFFFFF:0xFFFFFFFFFFFFFFFF`
  - `Null / Unspecified`: `0x0000000000000000:0x0000000000000000`

---

## 3. Wire Protocol Frame Layout

Every NSMP frame commences with an immutable 50-byte binary header formatted in big-endian network byte order:

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

### 3.1 Field Definitions
| Field Offset | Type | Name | Description |
| :--- | :--- | :--- | :--- |
| `0..1` | `u8[2]` | `Magic` | Must equal `0x4E, 0x58` ("NX") |
| `2` | `u8` | `Version` | Current version: `0x01` |
| `3` | `u8` | `PacketType` | Packet type (see Section 3.2) |
| `4` | `u8` | `Flags` | Control flags bitmask |
| `5` | `u8` | `HopLimit` | Decremented upon each relay hop (Default: 16) |
| `6` | `u8` | `HopCount` | Incremented upon each relay hop |
| `7` | `u8` | `Reserved` | Alignment byte; must be `0x00` |
| `8..15` | `u64` | `SourceHigh` | Most significant 64 bits of origin node address |
| `16..23` | `u64` | `SourceLow` | Least significant 64 bits of origin node address |
| `24..31` | `u64` | `DestHigh` | Most significant 64 bits of destination address |
| `32..39` | `u64` | `DestLow` | Least significant 64 bits of destination address |
| `40..43` | `u32` | `Sequence` | Monotonically increasing anti-replay sequence |
| `44..45` | `u16` | `PayloadLen` | Length of payload bytes (0 to 1,400) |
| `46..49` | `u32` | `Checksum` | CRC32 integrity checksum over header & payload |
| `50..N` | `u8[]` | `Payload` | Variable payload bytes |

### 3.2 Packet Types
- `0x00`: **Announce** &mdash; Broadcast beacon advertising presence and capabilities
- `0x01`: **Data** &mdash; End-to-end user application datagram
- `0x02`: **Ack** &mdash; Delivery or hop confirmation
- `0x03`: **RouteRequest** &mdash; Reactive path discovery query
- `0x04`: **RouteReply** &mdash; Path discovery confirmation
- `0x05`: **Telemetry** &mdash; RF signal report (RSSI, SNR, battery)
- `0x06`: **KeepAlive** &mdash; Link heartbeat

### 3.3 Flags
- `0x01`: `FLAG_ENCRYPTED` (ChaCha20-Poly1305 symmetric payload)
- `0x02`: `FLAG_ACK_REQUESTED` (Receipt acknowledgement requested)
- `0x04`: `FLAG_BROADCAST` (Flood to all neighbors)
- `0x08`: `FLAG_URGENT` (Expedited queueing)
- `0x10`: `FLAG_MULTI_PATH` (Permits multipath opportunistic dispersion)

---

## 4. Routing State Machine & Decision Logic

```text
Forwarding Decision:
IF Hash(src, seq) in AntiReplayCache:
    DROP (DropDuplicate)
ELSE:
    LearnReturnPath(src, hop_count + 1)
    IF dst == Self OR dst == Broadcast:
        DELIVER_LOCAL
    ELSE IF hop_limit <= 1:
        DROP (DropHopExceeded)
    ELSE:
        hop_limit -= 1
        hop_count += 1
        FORWARD_NEXT_HOP
```

---

## 5. Multi-Bearer Convergence Specification

The protocol frame is bearer-agnostic. The framing is identical across:
1. **LoRa Radio**: Transmitted via raw SPI FIFO on Semtech SX1262 / SX1276 transceivers.
2. **UDP Overlay**: Encapsulated directly within standard UDP datagrams for internet traversal.
3. **Layer-2 Ethernet**: Placed into custom EtherType frame (`0x88B5` / local experimental).
4. **Bluetooth Low Energy**: Dispatched across BLE GATT L2CAP credit-based channels.
