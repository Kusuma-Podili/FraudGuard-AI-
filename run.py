"""FraudGuard AI CLI Runner Script."""

import sys
import argparse
from backend.app.main import app
from simulator.cli import main as simulator_cli

def run_app(host: str = "127.0.0.1", port: int = 9000, reload: bool = False):
    import uvicorn
    print(f"\n=======================================================")
    print(f"  [+] FraudGuard AI Defense Portal & API Gateway")
    print(f"  [*] Portal URL:       http://{host}:{port}/")
    print(f"  [*] Interactive Docs: http://{host}:{port}/docs")
    print(f"  [*] Health Check:     http://{host}:{port}/api/v1/health")
    print(f"=======================================================\n")
    uvicorn.run("backend.app.main:app", host=host, port=port, reload=reload)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "simulator":
        sys.argv.pop(1)
        simulator_cli()
    else:
        parser = argparse.ArgumentParser(description="FraudGuard AI Application Runner")
        parser.add_argument("--port", "-p", type=int, default=9000, help="Port to run the application on (e.g. 5000, 7000, 9000)")
        parser.add_argument("--host", "-H", type=str, default="127.0.0.1", help="Host address (default: 127.0.0.1)")
        parser.add_argument("--reload", action="store_true", help="Enable live hot-reloading")
        
        if len(sys.argv) > 1 and sys.argv[1].isdigit():
            port_val = int(sys.argv.pop(1))
            run_app(port=port_val)
        else:
            args, _ = parser.parse_known_args()
            run_app(host=args.host, port=args.port, reload=args.reload)
