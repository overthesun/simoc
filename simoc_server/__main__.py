import argparse
from simoc_server.agent_model import AgentModel
from simoc_server import app

def run(debug=False, port=8000, run_local=False):
    addr = "0.0.0.0" if not run_local else "localhost"
    if debug:
        import os
        os.environ['PYTHONPATH'] = os.getcwd()
    agent_model = AgentModel(100, 100)
    app.run(addr, port=port, debug=debug)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SIMOC server.")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode.")
    parser.add_argument("--port", type=int, default=8000, help="Port to run server on. Default: 8000.")
    parser.add_argument("--run_local",  action="store_true", help="Run server locally.")

    args = parser.parse_args()
    run(debug=args.debug, port=args.port, run_local=args.run_local)
