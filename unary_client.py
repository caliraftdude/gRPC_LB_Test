import os
import grpc
import argparse
import time
import random
from colorama import Fore
from typing import Any

from logger import ColorLogger
from config import ClientConfig
from grpc_api import pb2, pb2_grpc, bidir, pb2_grpc_bidir

# Get logging
logger = ColorLogger("gRPC Client")


class BaseClient:
    def __init__(self, host:str, port:int = 50051, secure:bool = False):
        self.host = host
        self.port = port
        self.secure = secure
        self.cert_path = os.getenv("GRPC_CERT_PATH", "./certs/server.crt")
        self.channel = self._get_channel(secure)

        
    def _get_channel(self, secure:bool=False):
        if secure:
            try:
                # Load the trusted server certificate (CA certificate)
                with open(self.cert_path, 'rb') as f:
                    trusted_certs = f.read()
            
                # Create SSL credentials
                credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)

                # Create a secure channel
                return grpc.secure_channel(f'{self.host}:{self.port}', credentials)

            except FileNotFoundError:
                logger.error(f"The file {self.cert_path} was not found.")
            except PermissionError:
                logger.error(f"You do not have permission to read {self.cert_path}.")
            except OSError as e:
                logger.error(f"An unexpected OS error occurred: {e}")

        else:
            return grpc.insecure_channel(f'{self.host}:{self.server_port}')

        def _get_stub(self):
            # Ensure this gets written in inherited classes
            raise NotImplemented


class UnaryClient(BaseClient):
    def __init__(self, host:str, port:int = 50051, secure:bool = False):
        super().__init__(host, port, secure)
        self.stub = self._get_stub()

    def _get_stub(self):
        return pb2_grpc.UnaryStub(self.channel)

    def get_url(self, message:Any):
        """
        Client function to call the rpc for GetServerResponse
        """
        request = pb2.Message(message=message)
        return self.stub.GetServerResponse(request)
    

class BidirectionalClient:
    def __init__(self, host:str, port:int = 50051, secure:bool = False):
        super().__init__(host, port, secure)
        self.stub = self._get_stub()

    def _get_stub(self):
        return pb2_grpc_bidir.BidirectionalStub(self.channel)

    def run(self):
        """
        Client function to call the rpc for GetServerResponse
        """
        responses = self.stub.GetServerResponse(self.generate_messages())

        for response in responses:
            logger.log(f"Hello from the server received your {response.message}\n", color=Fore.GREEN)

    def generate_messages(self):
        messages = [
            self.make_message("First message"),
            self.make_message("Second message"),
            self.make_message("Third message"),
            self.make_message("Fourth message"),
            self.make_message("Fifth message"),
        ]

        for msg in messages:
            logger.log(f"Hello Server, sending you the {msg.message}\n", color=Fore.YELLOW)
            yield msg

    def make_message(self, message:Any):
        return bidir.Message( message=message )


def main():
    cs = ClientConfig( argparse.ArgumentParser(description="gRPC Client"), logger )
    args = cs.get_args()

    targets = [t.strip() for t in args.targets.split(",")]
    message = "Hello Server you there?"

    try:
        iteration = 0
        while True:
            iteration += 1
            logger.log(f"Starting iteration {iteration}", color=Fore.CYAN)

            for target in targets:
                logger.info(f"Trying to connect to {target}...")

                try:
                    if args.type == "unary":
                        client = UnaryClient(target, args.port, args.secure)
                        response = client.get_url(message)
                        logger.log(f"Response from {target}: {response.message}", color=Fore.GREEN)
                    elif args.type == "bidirectional":
                        client = BidirectionalClient(target, args.port, args.secure)
                        client.run()
                        logger.log(f"Completed bidirectional communication with {target}", color=Fore.GREEN)
                    else:
                        logger.log(f"Unknown service type: {args.service_type}", color=Fore.RED)

                except Exception as e:
                    logger.log(f"Failed to connect to {target}: {e}", color=Fore.RED)

                if args.delay_mode == "fixed":
                    time.sleep(args.delay)
                else:
                    delay = random.uniform(args.random_min, args.random_max)
                    logger.log(f"Sleeping for {delay:.2f} seconds", color=Fore.YELLOW)
                    time.sleep(delay)

            if args.repeat > 0 and iteration >= args.repeat:
                break
    except KeyboardInterrupt:
        logger.log("Client interrupted by user. Exiting...", color=Fore.MAGENTA)


if __name__ == '__main__':
    main()
