"""FraudGuard AI: Root Application Entry Point."""

import sys
import uvicorn
from backend.app.main import app

def start_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = True):
    """Start FraudGuard AI Decision Engine & Portal Server."""
    print(f"[*] Starting FraudGuard AI Enterprise Gateway on http://{host}:{port}")
    uvicorn.run("backend.app.main:app", host=host, port=port, reload=reload)

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    start_server(host=host, port=port)
