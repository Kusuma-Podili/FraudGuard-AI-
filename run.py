"""FraudGuard AI CLI Runner Script."""

import sys
import argparse
from backend.app.main import app
from simulator.cli import main as simulator_cli

def run_app():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "simulator":
        sys.argv.pop(1)
        simulator_cli()
    else:
        run_app()
