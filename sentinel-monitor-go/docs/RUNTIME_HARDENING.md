# SENTINEL Monitor Runtime Hardening v0.1

## Controls added

- Go monitor runs as non-root user `10001`.
- Health file path is controlled via `HEALTH_PATH`.
- Production compose uses fixed image digest placeholder.
- Production compose sets read-only filesystem.
- Production compose drops all Linux capabilities.
- Production compose uses tmpfs for health output.
- Production compose disables automatic image updates via labels.
- Docker build context excludes secrets and generated health files.

## Operational rule

Production deploys require an explicit release decision and a fixed image digest. Floating tags are not acceptable for evidence services.
