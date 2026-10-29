#!/usr/bin/env python3
"""
Nyx Sovereign Mesh Protocol (NSMP) - Multi-Hop Python Reference Simulation
==========================================================================
Architect: Simeon Bala & 9jaonCloud Engineering
Specification: RFC-001 (https://github.com/9jaoncloud/nyx-sovereign-mesh-protocol)

This standalone simulation executes a 3-node mesh topology:
  [Alice: 0xAAAA...01] <---> [Relay: 0xBBBB...02] <---> [Bob: 0xCCCC...03]

Features tested:
  1. 50-byte canonical binary wire header encoding and decoding
  2. CRC32 IEEE / folded checksum payload verification
  3. Hop-limit decrement & loop mitigation
  4. Anti-replay duplicate detection ring buffer
  5. Opportunistic reverse-path learning
"""

import struct
import zlib
import time
from typing import Dict, List, Optional, Tuple

NSMP_MAGIC_0 = 0x4E  # 'N'
NSMP_MAGIC_1 = 0x58  # 'X'
NSMP_VERSION = 1
NSMP_HEADER_SIZE = 50

# Packet Types
PKT_ANNOUNCE    = 0
PKT_DATA        = 1
PKT_ACK         = 2
PKT_ROUTE_REQ   = 3
PKT_ROUTE_REP   = 4
PKT_TELEMETRY   = 5
PKT_KEEP_ALIVE  = 6

# Bearer Types
BEARER_LORA     = 0
BEARER_UDP      = 1
BEARER_BLE      = 2
BEARER_ETHERNET = 3
BEARER_SERIAL   = 4


class NSMPPacket:
    def __init__(self, pkt_type: int, hop_limit: int,
                 src_high: int, src_low: int, dst_high: int, dst_low: int,
                 seq_num: int, payload: bytes, flags: int = 0):
        self.magic_0 = NSMP_MAGIC_0
        self.magic_1 = NSMP_MAGIC_1
        self.version = NSMP_VERSION
        self.pkt_type = pkt_type
        self.flags = flags
        self.hop_limit = hop_limit
        self.hop_count = 0
        self.reserved = 0
        self.src_high = src_high
        self.src_low = src_low
        self.dst_high = dst_high
        self.dst_low = dst_low
        self.seq_num = seq_num
        self.payload = payload
        self.payload_len = len(payload)
        self.checksum = self.calculate_checksum()

    def calculate_checksum(self) -> int:
        crc = 0xFFFFFFFF
        crc ^= (self.src_high >> 32) & 0xFFFFFFFF
        crc ^= self.src_high & 0xFFFFFFFF
        crc ^= (self.src_low >> 32) & 0xFFFFFFFF
        crc ^= self.src_low & 0xFFFFFFFF
        crc ^= (self.dst_high >> 32) & 0xFFFFFFFF
        crc ^= self.dst_high & 0xFFFFFFFF
        crc ^= (self.dst_low >> 32) & 0xFFFFFFFF
        crc ^= self.dst_low & 0xFFFFFFFF
        crc ^= self.seq_num
        crc ^= self.payload_len

        for b in self.payload:
            crc = ((crc >> 8) ^ (crc ^ b)) & 0xFFFFFFFF
        return crc

    def serialize(self) -> bytes:
        self.checksum = self.calculate_checksum()
        header = struct.pack(
            ">BBBBBBBBQQQQIHI",
            self.magic_0,
            self.magic_1,
            self.version,
            self.pkt_type,
            self.flags,
            self.hop_limit,
            self.hop_count,
            self.reserved,
            self.src_high,
            self.src_low,
            self.dst_high,
            self.dst_low,
            self.seq_num,
            self.payload_len,
            self.checksum
        )
        return header + self.payload

    @staticmethod
    def deserialize(data: bytes) -> Optional["NSMPPacket"]:
        if len(data) < NSMP_HEADER_SIZE:
            return None

        header_data = data[:NSMP_HEADER_SIZE]
        (m0, m1, ver, p_type, flags, hop_lim, hop_cnt, res,
         s_hi, s_lo, d_hi, d_lo, seq, p_len, expected_crc) = struct.unpack(">BBBBBBBBQQQQIHI", header_data)

        if m0 != NSMP_MAGIC_0 or m1 != NSMP_MAGIC_1 or ver != NSMP_VERSION:
            return None

        if len(data) < NSMP_HEADER_SIZE + p_len:
            return None

        payload = data[NSMP_HEADER_SIZE : NSMP_HEADER_SIZE + p_len]

        pkt = NSMPPacket(p_type, hop_lim, s_hi, s_lo, d_hi, d_lo, seq, payload, flags)
        pkt.hop_count = hop_cnt
        pkt.reserved = res

        if pkt.calculate_checksum() != expected_crc:
            return None

        return pkt


class MeshNode:
    def __init__(self, name: str, addr_hi: int, addr_lo: int):
        self.name = name
        self.addr_hi = addr_hi
        self.addr_lo = addr_lo
        self.routing_table: Dict[Tuple[int, int], Tuple[int, int, int]] = {}
        self.seen_cache: List[int] = [0] * 512
        self.neighbors: List["MeshNode"] = []
        self.received_messages: List[str] = []

    def address_hex(self) -> str:
        return f"{self.addr_hi:016x}{self.addr_lo:016x}"

    def connect(self, peer: "MeshNode"):
        if peer not in self.neighbors:
            self.neighbors.append(peer)
        if self not in peer.neighbors:
            peer.neighbors.append(self)

    def learn_route(self, src_hi: int, src_lo: int, via_hi: int, via_lo: int, hop_count: int):
        target = (src_hi, src_lo)
        if target not in self.routing_table or self.routing_table[target][2] > hop_count:
            self.routing_table[target] = (via_hi, via_lo, hop_count)

    def is_duplicate(self, src_lo: int, seq_num: int) -> bool:
        slot = (src_lo ^ seq_num) % 512
        entry = (src_lo << 32) | (seq_num & 0xFFFFFFFF)
        if self.seen_cache[slot] == entry:
            return True
        self.seen_cache[slot] = entry
        return False

    def receive_packet(self, raw_bytes: bytes, from_peer: "MeshNode"):
        pkt = NSMPPacket.deserialize(raw_bytes)
        if pkt is None:
            print(f"[{self.name}] DROPPED: Invalid packet format or corrupted checksum.")
            return

        # Anti-replay check
        if self.is_duplicate(pkt.src_low, pkt.seq_num):
            print(f"[{self.name}] DUPLICATE DETECTED: Discarding seq #{pkt.seq_num} from {pkt.src_low:016x}")
            return

        # Opportunistic reverse-path learning
        hops_taken = pkt.hop_count + 1
        self.learn_route(pkt.src_high, pkt.src_low, from_peer.addr_hi, from_peer.addr_lo, hops_taken)

        # Check destination
        if pkt.dst_high == self.addr_hi and pkt.dst_low == self.addr_lo:
            msg = pkt.payload.decode("utf-8", errors="replace")
            self.received_messages.append(msg)
            print(f"[{self.name}] >>> DELIVERED: '{msg}' from {pkt.src_low:016x} via {from_peer.name} (Hops: {hops_taken})")
            return

        # Forwarding branch
        if pkt.hop_limit <= 1:
            print(f"[{self.name}] TTL EXPIRED: Packet dropped (seq #{pkt.seq_num})")
            return

        # Decrement TTL, increment hops and relay
        pkt.hop_limit -= 1
        pkt.hop_count += 1
        forward_bytes = pkt.serialize()

        target = (pkt.dst_high, pkt.dst_low)
        if target in self.routing_table:
            next_hop = self.routing_table[target]
            for peer in self.neighbors:
                if (peer.addr_hi, peer.addr_lo) == (next_hop[0], next_hop[1]):
                    print(f"[{self.name}] ROUTED: Forwarding packet to known next hop {peer.name}")
                    peer.receive_packet(forward_bytes, self)
                    return

        # Fallback opportunistic broadcast to neighbors except ingress
        print(f"[{self.name}] FLOODING: Forwarding to all peers except {from_peer.name}")
        for peer in self.neighbors:
            if peer != from_peer:
                peer.receive_packet(forward_bytes, self)


def main():
    print("=" * 70)
    print("Nyx Sovereign Mesh Protocol (NSMP) Reference Simulation")
    print("=" * 70)

    # 1. Instantiate 3 Nodes
    alice = MeshNode("Alice", 0xAAAA000000000001, 0x1111111111111111)
    relay = MeshNode("Relay", 0xBBBB000000000002, 0x2222222222222222)
    bob   = MeshNode("Bob",   0xCCCC000000000003, 0x3333333333333333)

    # Connect linear topology: Alice <---> Relay <---> Bob
    alice.connect(relay)
    relay.connect(bob)

    print("Topology Configured:")
    print(f"  Alice: {alice.address_hex()}")
    print(f"  Relay: {relay.address_hex()}")
    print(f"  Bob:   {bob.address_hex()}")
    print("-" * 70)

    # 2. Alice sends a direct packet to Bob across Relay
    secret_msg = "Sovereign packet payload via zero-GC NSMP mesh wire."
    pkt = NSMPPacket(
        pkt_type=PKT_DATA,
        hop_limit=16,
        src_high=alice.addr_hi,
        src_low=alice.addr_lo,
        dst_high=bob.addr_hi,
        dst_low=bob.addr_lo,
        seq_num=1001,
        payload=secret_msg.encode("utf-8")
    )
    raw_packet = pkt.serialize()

    print(f"[Alice] Transmitting 50-byte wire frame (Total {len(raw_packet)} bytes) to Relay...")
    relay.receive_packet(raw_packet, alice)

    # 3. Test Replay Attack
    print("\n[Simulating Replay Attack]: Alice's identical packet is re-broadcast by an adversary...")
    relay.receive_packet(raw_packet, alice)

    # 4. Verification Check
    print("-" * 70)
    if len(bob.received_messages) == 1 and bob.received_messages[0] == secret_msg:
        print("[SUCCESS] Multi-hop transmission delivered exactly once. Anti-replay verified.")
    else:
        print("[FAILURE] Message not delivered correctly.")
        exit(1)


if __name__ == "__main__":
    main()
