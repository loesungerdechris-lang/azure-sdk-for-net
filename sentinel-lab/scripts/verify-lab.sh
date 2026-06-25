#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT_DIR"

docker compose -f docker-compose.lab.yml ps

docker logs --tail 50 sentinel-lab-monitor

echo "SENTINEL lab verification completed"
