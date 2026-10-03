# SENTINEL Monitor Go

Go-first runtime monitor for SENTINEL self-tests and health reporting.

## Status

Current repository: `loesungerdechris-lang/azure-sdk-for-net`
Intended public name: `sentinel-monitor-go`

## Local checks

```bash
go test ./...
go build ./cmd/sentinel-monitor
```

## Release gate

Pull requests, changes on main, manual validation and weekly runs execute Go tests,
Govulncheck and an offline image scan. The build uses Go 1.27.1 and digest-pinned
Go/Alpine base images. HIGH or CRITICAL findings stop the release, including
findings without an available fix.

A release tag must match `sentinel-monitor-go/vMAJOR.MINOR.PATCH` and point to a
commit already on main. Only a successful validation and scan allow the publish
job to copy the original OCI archive to GHCR, preserving its digest, SBOM and
provenance. The job verifies artifact checksums and requires a scan less than
24 hours old. Version and commit aliases are created after Cosign signing,
signature verification and upload of the signed evidence.

Validation and scan reports, OCI archives and signed evidence are retained as
GitHub Actions artifacts for 90 days. Runtime configuration in the production
Compose file still requires the verified image digest from a successful release.
