#!/usr/bin/env bash
set -euo pipefail

# External IP
BASE_URL="http://34.139.134.144"

echo "=== E2E demo: Spot Management ==="

echo "[1] Health check..."
curl -sf "$BASE_URL/health" > /dev/null
echo "OK"

echo "[2] Create a test study spot..."
CREATE_RESP=$(curl -s -X POST "$BASE_URL/study-spots" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "E2E Test Spot",
    "city": "NYC",
    "has_wifi": true
  }')
echo "Create response:"
echo "$CREATE_RESP"

echo "[3] List study spots..."
LIST_RESP=$(curl -s "$BASE_URL/study-spots")
echo "$LIST_RESP" | jq '.' || echo "$LIST_RESP"

echo "=== E2E script completed ==="
