# SENTINEL Monitor Go Security Policy

## Scope

This module contains the SENTINEL runtime monitor bootstrap. Security-sensitive areas include self-tests, health reporting, alerting and future chain connectivity.

## Reporting

Do not publish suspected vulnerabilities, exposed tokens or operational details in public issues. Report privately to the repository owner.

## Rules

- No secrets or private keys in Git.
- Production images must use fixed digests.
- The monitor must run as non-root.
- Production containers must drop Linux capabilities where possible.
- Automatic image updates must not update production evidence services.
- Health output must be written only to an explicitly configured writable path.
