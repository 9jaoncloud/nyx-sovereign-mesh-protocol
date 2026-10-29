/*
 * nsmp.h — Nyx Sovereign Mesh Protocol (NSMP) Universal C Header
 * Standard Reference Interface for NSMP v1.0
 * 
 * Copyright (c) 2026 Simeon Bala & 9jaonCloud Engineering.
 * Licensed under the Business Source License 1.1 with Reciprocal Community Grant.
 */

#ifndef NSMP_H
#define NSMP_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define NSMP_MAGIC_0 0x4E /* 'N' */
#define NSMP_MAGIC_1 0x58 /* 'X' */
#define NSMP_PROTOCOL_VERSION 1
#define NSMP_HEADER_SIZE 50
#define NSMP_MAX_PAYLOAD_SIZE 1400
#define NSMP_MAX_HOPS 16

/* Flags */
#define NSMP_FLAG_ENCRYPTED     0x01
#define NSMP_FLAG_ACK_REQUESTED 0x02
#define NSMP_FLAG_BROADCAST     0x04
#define NSMP_FLAG_URGENT        0x08
#define NSMP_FLAG_MULTI_PATH    0x10

typedef enum {
    NSMP_TYPE_ANNOUNCE      = 0,
    NSMP_TYPE_DATA          = 1,
    NSMP_TYPE_ACK           = 2,
    NSMP_TYPE_ROUTE_REQUEST = 3,
    NSMP_TYPE_ROUTE_REPLY   = 4,
    NSMP_TYPE_TELEMETRY     = 5,
    NSMP_TYPE_KEEP_ALIVE    = 6
} nsmp_packet_type_t;

typedef enum {
    NSMP_BEARER_LORA_RADIO  = 0,
    NSMP_BEARER_UDP_OVERLAY = 1,
    NSMP_BEARER_BLUETOOTH_LE= 2,
    NSMP_BEARER_ETHERNET    = 3,
    NSMP_BEARER_SERIAL_UART = 4
} nsmp_bearer_type_t;

typedef struct {
    uint64_t hi;
    uint64_t lo;
} nsmp_address_t;

#pragma pack(push, 1)
typedef struct {
    uint8_t  magic_0;
    uint8_t  magic_1;
    uint8_t  version;
    uint8_t  packet_type;
    uint8_t  flags;
    uint8_t  hop_limit;
    uint8_t  hop_count;
    uint8_t  reserved;
    uint64_t src_hi;
    uint64_t src_lo;
    uint64_t dst_hi;
    uint64_t dst_lo;
    uint32_t seq_num;
    uint16_t payload_len;
    uint32_t checksum;
} nsmp_header_t;
#pragma pack(pop)

typedef enum {
    NSMP_ACTION_DELIVER_LOCALLY   = 0,
    NSMP_ACTION_FORWARD_NEXT_HOP  = 1,
    NSMP_ACTION_DROP_DUPLICATE    = 2,
    NSMP_ACTION_DROP_HOP_EXCEEDED = 3
} nsmp_action_t;

/* Address Utilities */
static inline nsmp_address_t nsmp_address_make(uint64_t hi, uint64_t lo) {
    nsmp_address_t addr = { hi, lo };
    return addr;
}

static inline bool nsmp_address_is_broadcast(nsmp_address_t addr) {
    return (addr.hi == 0xFFFFFFFFFFFFFFFFULL && addr.lo == 0xFFFFFFFFFFFFFFFFULL);
}

static inline bool nsmp_address_is_equal(nsmp_address_t a, nsmp_address_t b) {
    return (a.hi == b.hi && a.lo == b.lo);
}

#ifdef __cplusplus
}
#endif

#endif /* NSMP_H */
