#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT_DIR"

docker compose -f docker-compose.lab.yml up --build -d

echo "SENTINEL lab started"
echo "Anvil RPC: http://127.0.0.1:8545"
echo "IPFS API:  http://127.0.0.1:5001"
echo "Monitor:   sentinel-lab-monitor"
