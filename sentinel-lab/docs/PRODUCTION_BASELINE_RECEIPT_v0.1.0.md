# SENTINEL Production Baseline Receipt

**Genesis Release:** v0.1.0 Go Implementation  
**Status:** AWAITING_DIGESTS  
**Date:** 2026-06-24  
**Issuer:** Akira Security GmbH / SENTINEL Governance Layer

## 1. Governance and System Purpose

This receipt documents the initial cryptographic production baseline for SENTINEL Core and SENTINEL Monitor. It is intended to provide a reproducible chain-of-custody reference for future deployments, audits and release decisions.

The receipt supports audit preparation for requirements related to robustness, cybersecurity, technical documentation and traceability. It does not by itself constitute legal certification or regulatory approval.

## 2. Source Baseline

| Component | Version | Git Commit | CI Run ID | Status |
|---|---:|---|---|---|
| SENTINEL Core | v0.1.0 | INSERT_CORE_COMMIT | INSERT_CORE_RUN_ID | AWAITING_GREEN_CI |
| SENTINEL Monitor | v0.1.0 | INSERT_MONITOR_COMMIT | INSERT_MONITOR_RUN_ID | AWAITING_GREEN_CI |

## 3. Immutable Deployment Artifacts

Production deployments must reference immutable image digests. Floating tags such as `latest` are not valid production references.

| Artifact | Registry reference | Signature status | Scan status |
|---|---|---|---|
| SENTINEL Core | ghcr.io/loesungerdechris-lang/sentinel-core-go@sha256:INSERT_CORE_DIGEST | AWAITING_COSIGN | AWAITING_SCAN |
| SENTINEL Monitor | ghcr.io/loesungerdechris-lang/sentinel-monitor-go@sha256:INSERT_MONITOR_DIGEST | AWAITING_COSIGN | AWAITING_SCAN |

## 4. Runtime Hardening Constraints

A deployment is not covered by this baseline if it weakens the runtime constraints below.

| Control | Required state |
|---|---|
| User | non-root UID/GID 10001 |
| Root filesystem | read-only |
| Linux capabilities | dropped where technically possible |
| Writable runtime path | tmpfs only |
| Production image reference | fixed digest only |
| Automatic production updates | disabled |
| Secret handling | no secrets committed to Git |

## 5. Toolchain Baseline

| Tool | Required baseline |
|---|---|
| Go | 1.23.10 or later patched baseline |
| Container build | GitHub Actions release workflow |
| Vulnerability scan | govulncheck and Trivy |
| Signature | cosign keyless signature via GitHub OIDC |
| SBOM | generated during release workflow |

## 6. Policy Gate Transition

| Gate | Meaning | State |
|---|---|---|
| G0_OBSERVE | baseline observed in CI/lab | ACTIVE |
| G1_BASELINE_ESTABLISHED | immutable source and artifact baseline documented | PENDING_DIGESTS |

## 7. Completion Checklist

- [ ] Core PR merged
- [ ] Monitor PR merged
- [ ] Release tag created
- [ ] Core commit inserted
- [ ] Monitor commit inserted
- [ ] CI run IDs inserted
- [ ] Image digests inserted
- [ ] Trivy status inserted
- [ ] Cosign signature status inserted
- [ ] Production compose updated to fixed digest
- [ ] Final receipt committed

## 8. Claim-Safety Statement

This receipt proves the integrity references of the documented source commits, build process and container image digests once completed. It does not claim that the software is free of all vulnerabilities. It establishes a reproducible, reviewable and auditable baseline for controlled deployment.
