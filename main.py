"""FraudGuard AI: Root Application Entry Point."""

import sys
import argparse
import uvicorn
from backend.app.main import app

def start_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = True):
    """Start FraudGuard AI Decision Engine & Portal Server."""
    print(f"\n=======================================================")
    print(f"  🛡️ FraudGuard AI Defense Portal & API Gateway")
    print(f"  🔗 Portal URL:       http://{host}:{port}/")
    print(f"  📚 Interactive Docs: http://{host}:{port}/docs")
    print(f"  🩺 Health Check:     http://{host}:{port}/api/v1/health")
    print(f"=======================================================\n")
    uvicorn.run("backend.app.main:app", host=host, port=port, reload=reload)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FraudGuard AI Server")
    parser.add_argument("--port", "-p", type=int, default=8000, help="Port to run the application on (e.g. 8000, 8500, 9000)")
    parser.add_argument("--host", "-H", type=str, default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    parser.add_argument("--no-reload", action="store_true", help="Disable hot-reloading")
    
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port_val = int(sys.argv.pop(1))
        start_server(port=port_val)
    else:
        args, _ = parser.parse_known_args()
        start_server(host=args.host, port=args.port, reload=not args.no_reload)
