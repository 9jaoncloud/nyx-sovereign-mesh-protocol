/*
 * nsmp_packet_example.c — Nyx Sovereign Mesh Protocol (NSMP) Reference Packet C Example
 * 
 * Demonstrates:
 * 1. Structuring an NSMP wire header matching RFC-001
 * 2. Address initialization & comparison
 * 3. Serialization to wire buffer
 * 
 * Compile:
 *   gcc -O2 -I../include nsmp_packet_example.c -o nsmp_example
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "../include/nsmp.h"

static void hex_dump(const uint8_t *data, size_t len) {
    for (size_t i = 0; i < len; i++) {
        printf("%02X ", data[i]);
        if ((i + 1) % 16 == 0) printf("\n");
        else if ((i + 1) % 8 == 0) printf("  ");
    }
    printf("\n");
}

int main(void) {
    printf("=================================================================\n");
    printf("Nyx Sovereign Mesh Protocol (NSMP) C Construction Example\n");
    printf("=================================================================\n\n");

    /* 1. Define Node Addresses */
    nsmp_address_t alice = nsmp_address_make(0xAAAA000000000001ULL, 0x1111111111111111ULL);
    nsmp_address_t bob   = nsmp_address_make(0xCCCC000000000003ULL, 0x3333333333333333ULL);

    printf("Header Struct Size: %zu bytes (Packed)\n", sizeof(nsmp_header_t));

    /* 2. Prepare Payload */
    const char *payload_text = "NSMP-ZERO-GC-EMBEDDED-FRAME";
    uint16_t payload_len = (uint16_t)strlen(payload_text);

    /* 3. Construct Header */
    nsmp_header_t hdr;
    memset(&hdr, 0, sizeof(hdr));

    hdr.magic_0     = NSMP_MAGIC_0;
    hdr.magic_1     = NSMP_MAGIC_1;
    hdr.version     = NSMP_PROTOCOL_VERSION;
    hdr.packet_type = NSMP_TYPE_DATA;
    hdr.flags       = NSMP_FLAG_ACK_REQUESTED;
    hdr.hop_limit   = NSMP_MAX_HOPS;
    hdr.hop_count   = 0;
    hdr.reserved    = 0;

    hdr.src_hi      = alice.hi;
    hdr.src_lo      = alice.lo;
    hdr.dst_hi      = bob.hi;
    hdr.dst_lo      = bob.lo;

    hdr.seq_num     = 0x000003E9; /* 1001 */
    hdr.payload_len = payload_len;
    hdr.checksum    = 0xCAFEBABE; /* Example checksum */

    /* 4. Assemble Wire Buffer */
    uint8_t wire[NSMP_MAX_PAYLOAD_SIZE + sizeof(nsmp_header_t)];
    memcpy(wire, &hdr, sizeof(nsmp_header_t));
    memcpy(wire + sizeof(nsmp_header_t), payload_text, payload_len);

    size_t total_wire_len = sizeof(nsmp_header_t) + payload_len;

    printf("Total Wire Length: %zu bytes\n\n", total_wire_len);
    printf("Hex Dump of Wire Frame:\n");
    printf("-----------------------------------------------------------------\n");
    hex_dump(wire, total_wire_len);
    printf("-----------------------------------------------------------------\n");

    /* 5. Address Validation */
    if (nsmp_address_is_broadcast(bob)) {
        printf("Destination is BROADCAST\n");
    } else {
        printf("Destination is UNICAST (Bob: 0x%016llX...)\n", (unsigned long long)bob.hi);
    }

    printf("\n[SUCCESS] NSMP Packet constructed and validated successfully.\n");
    return 0;
}
