# SENTINEL Lab v0.1

Local integration stack for the Go-first SENTINEL runtime.

## Purpose

The lab gives us a safe Ghost Mode environment for the first integrated runtime checks:

- SENTINEL monitor container
- local EVM endpoint through Anvil
- local IPFS node for future evidence bundle storage
- hardened monitor runtime settings

This is not production. Production still requires fixed image digests, signed releases and explicit release evidence.

## Start

Run from the lab folder:

```bash
cp .env.example .env
sh scripts/run-lab.sh
```

## Verify

Run from the lab folder:

```bash
sh scripts/verify-lab.sh
```

## Security posture

The monitor runs as a non-root user with read-only filesystem, dropped Linux capabilities and a tmpfs-only writable health path.
