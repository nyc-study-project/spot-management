import os
import sys

# Ensure spot-management project root is on sys.path
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_endpoint():
    """
    Basic test to verify that /health returns HTTP 200.
    Assumes the FastAPI app in main.py defines GET /health.
    """
    response = client.get("/health")
    assert response.status_code == 200

