# SENTINEL Baseline Steps v0.1

1. Review both open PRs.
2. Wait until CI and security scans are green.
3. Merge the core PR.
4. Merge the monitor PR.
5. Create the release tags.
6. Copy the commit values, workflow run IDs and image digest values from GitHub Actions.
7. Complete the production baseline receipt.
8. Replace the production compose placeholder with the fixed digest.
9. Commit the completed receipt.

Production rule: no floating image references for evidence services.
