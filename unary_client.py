import sys
import grpc
import argparse
import time
import random
from datetime import datetime
from colorama import Fore, Style, init

import unary_pb2_grpc as pb2_grpc
import unary_pb2 as pb2


class UnaryClient:
    """
    Client for gRPC functionality
    """

    def __init__(self, host, port=50051):
        self.host = host
        self.server_port = port
        self.channel = grpc.insecure_channel(f'{self.host}:{self.server_port}')
        self.stub = pb2_grpc.UnaryStub(self.channel)

    def get_url(self, message):
        """
        Client function to call the rpc for GetServerResponse
        """
        request = pb2.Message(message=message)
        return self.stub.GetServerResponse(request)

def log(message, color=Fore.WHITE):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{color}[{timestamp}] {message}{Style.RESET_ALL}")

def get_cmd_args():
    # Argument parsing
    parser = argparse.ArgumentParser(description="gRPC Unary Client with Looping and Delay Options")
    parser.add_argument("--targets", type=str, required=True,
                        help="Comma-separated list of server addresses (e.g., localhost:50051,localhost:50052)")
    parser.add_argument("--repeat", type=int, default=1,
                        help="Number of times to loop through all targets (0 for infinite)")
    parser.add_argument("--delay-mode", choices=["fixed", "random"], default="fixed",
                        help="Delay mode between requests: 'fixed' or 'random'")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="Fixed delay in seconds (used if delay-mode is 'fixed')")
    parser.add_argument("--random-min", type=float, default=0.5,
                        help="Minimum random delay in seconds (used if delay-mode is 'random')")
    parser.add_argument("--random-max", type=float, default=2.0,
                        help="Maximum random delay in seconds (used if delay-mode is 'random')")
    args = parser.parse_args()

    # Validate delay values
    if args.delay_mode == "fixed" and not (0 <= args.delay <= 600):
        log("Fixed delay must be between 0 and 600 seconds.", color=Fore.RED)
        exit(1)
    if args.delay_mode == "random" and args.random_min > args.random_max:
        log("Random delay minimum cannot be greater than maximum.", color=Fore.RED)
        exit(1)
    
    return args

def main():
    args = get_cmd_args()
    targets = [t.strip() for t in args.targets.split(",")]
    message = "Hello Server you there?"

    try:
        iteration = 0
        while True:
            iteration += 1
            log(f"Starting iteration {iteration}", color=Fore.CYAN)
            for target in targets:
                log(f"Trying to connect to {target}...")

                try:
                    client = UnaryClient(target)
                    response = client.get_url(message)
                    log(f"Response from {target}: {response}", color=Fore.GREEN)
                except Exception as e:
                    log(f"Failed to connect to {target}: {e}", color=Fore.RED)

                if args.delay_mode == "fixed":
                    time.sleep(args.delay)
                else:
                    delay = random.uniform(args.random_min, args.random_max)
                    log(f"Sleeping for {delay:.2f} seconds", color=Fore.YELLOW)
                    time.sleep(delay)
            if args.repeat > 0 and iteration >= args.repeat:
                break
    except KeyboardInterrupt:
        log("Client interrupted by user. Exiting...", color=Fore.MAGENTA)


if __name__ == '__main__':
    # Initialize colorama
    init(autoreset=True)
    main()
