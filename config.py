
import os
import argparse
import logging
from argparse import ArgumentParser
from colorama import Fore
from typing import Any

from logger import ColorLogger


class ConfigGeneralException(Exception):
    pass


class BaseConfig:
    def __init__(self, parser: ArgumentParser, log:ColorLogger):
        self.log = log
        log.info("BaseConfig init")
        parser.add_argument("--type", type=str, choices=["unary", "bidirectional"], default="unary", help="Type of gRPC service to run: 'unary' or 'bidirectional'")
        parser.add_argument("--secure", action="store_true", required=False, help="Use secure gRPC channel with SSL/TLS")
        parser.add_argument("--port", type=int, default=50051, help="Port to bind to (server) or connect on (client)")

    def parse_cmd_args(self, parser: ArgumentParser) -> Any:
        try:
            args = parser.parse_args()
            return args
        
        except SystemExit as e:
            if e.code == 1:  # general error
                self.log.error(f"General error while parsing: {e}")
            elif e.code == 2: #parsing error
                self.log.error(f"Argument parsing failed: {e}")

            raise ConfigGeneralException
        
    def get_args(self):
        pass
    

class ServerConfig(BaseConfig):
    def __init__(self, parser: ArgumentParser, log:ColorLogger):
        super().__init__( parser, log )
        log.info("ServerConfig init")

        parser.add_argument("--ip", type=str, help="IP address to bind to")


        self.args = self.parse_cmd_args(parser)

        self.ip = self.args.ip or os.getenv("GRPC_SERVER_IP", "0.0.0.0")
        self.port = self.args.port or int(os.getenv("GRPC_SERVER_PORT", "50051"))
        self.type = self.args.type or os.getenv("GRPC_SERVICE_TYPE", "unary").lower()


    def get_args(self) -> tuple[str, str, str]:
        return self.ip, self.port, self.type


class ClientConfig(BaseConfig):
    def __init__(self, parser: ArgumentParser, log:ColorLogger):
        super().__init__( parser, log )
        log.info("ClientConfig init")

        parser.add_argument("--targets", type=str, required=True, help="Comma-separated list of server addresses (e.g., localhost:50051,localhost:50052)")
        parser.add_argument("--repeat", type=int, default=1, help="Number of times to loop through all targets (0 for infinite)")
        parser.add_argument("--delay-mode", choices=["fixed", "random"], default="fixed", help="Delay mode between requests: 'fixed' or 'random'")
        parser.add_argument("--delay", type=float, default=1.0, help="Fixed delay in seconds (used if delay-mode is 'fixed')")
        parser.add_argument("--random-min", type=float, default=0.5, help="Minimum random delay in seconds (used if delay-mode is 'random')")
        parser.add_argument("--random-max", type=float, default=2.0, help="Maximum random delay in seconds (used if delay-mode is 'random')")

        self.args = self.parse_cmd_args(parser)

        # Check for port env var
        self.port = self.args.port or int(os.getenv("GRPC_CLIENT_PORT", "50051"))
        
        # Validate delay values
        if self.args.delay_mode == "fixed" and not (0 <= self.args.delay <= 600):
            log.error("Fixed delay must be between 0 and 600 seconds.", color=Fore.RED)
            exit(1)
        if self.args.delay_mode == "random" and self.args.random_min > self.args.random_max:
            log.error("Random delay minimum cannot be greater than maximum.", color=Fore.RED)
            exit(1)
      
    
    def get_args(self) -> Any:
        return self.args 


######################################################################################################
## For testing
def main():
    sc = ServerConfig( argparse.ArgumentParser(description="gRPC Server"), ColorLogger("Config") )
    ip, port, type = sc.get_args()

    cs = ClientConfig( argparse.ArgumentParser(description="gRPC Client"),  ColorLogger("Config") )
    args = cs.get_args()

if __name__ == '__main__':
    main()