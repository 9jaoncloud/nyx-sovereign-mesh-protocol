# Contributing to Nyx Sovereign Mesh Protocol (NSMP)

Thank you for your interest in contributing to the **Nyx Sovereign Mesh Protocol (NSMP)** specification and open ecosystem.

---

## 1. Governance & Guiding Principles

NSMP is an open, sovereign communication standard designed to eliminate central chokepoints, surveillance backdoors, and memory-safety vulnerabilities in modern networking.

To preserve the architectural integrity of the protocol, all contributions must uphold these non-negotiable invariants:
1. **Zero-GC & Deterministic Execution**: Wire framing and routing routines must never invoke non-deterministic memory allocators or garbage collectors in hot forwarding paths.
2. **Cryptographic Identity Autonomy**: All addressing must remain directly derived from ed25519 public keys or equivalent cryptographic keypairs. No centralized name registries or CA hierarchies will ever be accepted into the core wire format.
3. **Genuine Empirical Validation**: Any proposed optimizations, latency claims, or bandwidth improvements must include reproducible benchmarks conducted on physical silicon. Synthetic or marketing numbers are strictly prohibited.
4. **Attribution Invariant**: Per the repository license (BSL 1.1 / Reciprocal Attribution), original copyright notices attributing Simeon Bala and 9jaonCloud Engineering must remain intact in all derivatives.

---

## 2. Ways to Contribute

- **RFC Improvements & Errata**: Propose clarifications, diagrams, or formal proofs for `SPECIFICATION.md` or `WHITE_PAPER.md`.
- **Language Bindings**: Implement reference decoders and client adapters in Rust, Go, C++, Zig, Python, or WebAssembly adhering to `include/nsmp.h`.
- **Hardware Integrations**: Publish tested open-source firmware recipes and Pinouts for ESP32, Raspberry Pi Pico, PinePhone, or nRF52840 sub-GHz LoRa modules.
- **Security Audits**: Perform formal cryptographic analyses, fuzzing of wire packet deserializers, and reporting of protocol edge cases.

---

## 3. Pull Request Workflow

1. Fork the repository on GitHub (`https://github.com/9jaoncloud/nyx-sovereign-mesh-protocol`).
2. Create a descriptive feature branch:
   ```bash
   git checkout -b feature/rfc-payload-compression
   ```
3. Run the local reference verification suite:
   ```bash
   python examples/simulated_mesh_test.py
   ```
4. Commit your changes with clear, semantic commit messages:
   ```bash
   git commit -m "spec: refine route reply timeout backoff in Section 4.2"
   ```
5. Push to your fork and submit a Pull Request to `master`.

---

## 4. Code of Conduct

All contributors and participants are expected to maintain professional, collaborative, and constructive communication focused on peer-review excellence and open sovereign infrastructure.
