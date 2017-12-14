import argparse
from simoc_server.serialize.serializer import JsonSerializer, MsgPackSerializer, set_serializer
from simoc_server.agent_model import AgentModel
from simoc_server import app

def run(debug=False, port=8000, run_local=False, threaded=True, use_json=False):
    addr = "0.0.0.0" if not run_local else "localhost"
    if debug:
        import os
        os.environ['PYTHONPATH'] = os.getcwd()
    if use_json:
        set_serializer(JsonSerializer)
    app.run(addr, port=port, debug=debug, threaded=threaded)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SIMOC server.")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode.")
    parser.add_argument("--port", type=int, default=8000, help="Port to run server on. Default: 8000.")
    parser.add_argument("--run_local",  action="store_true", help="Run server locally.")
    parser.add_argument("--do_not_thread",  action="store_true", help="Do not run flask app threaded.")
    parser.add_argument("--use_json",  action="store_true", help="Use json to serialize rest messages, defaults to."
        "MessagePack")

    args = parser.parse_args()
    run(debug=args.debug, port=args.port, run_local=args.run_local, threaded=(not args.do_not_thread), use_json=args.use_json)
