import grpc
import argparse
import time
import random
from colorama import Fore

from logger import ColorLogger
from config import ClientConfig
from grpc_api import pb2, pb2_grpc, bidir, pb2_grpc_bidir

# Get logging
logger = ColorLogger("gRPC Client")

class UnaryClient:
    """
    Client for gRPC functionality
    """

    def __init__(self, host, secure=False, port=50051):
        self.host = host
        self.server_port = port
        self.channel = self._set_up_channel(secure)
        self.stub = pb2_grpc.UnaryStub(self.channel)

    def _set_up_channel(self, secure=False):
        if secure:
            try:
                cert_path = "./certs/server.crt"

                # Load the trusted server certificate (CA certificate)
                with open(cert_path, 'rb') as f:
                    trusted_certs = f.read()
            
                # Create SSL credentials
                credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)

                # Create a secure channel
                return grpc.secure_channel(f'{self.host}:{self.server_port}', credentials)

            except FileNotFoundError:
                logger.error(f"The file {cert_path} was not found.")
            except PermissionError:
                logger.error(f"You do not have permission to read {cert_path}.")
            except OSError as e:
                logger.error(f"An unexpected OS error occurred: {e}")

        else:
            return grpc.insecure_channel(f'{self.host}:{self.server_port}')

    def get_url(self, message):
        """
        Client function to call the rpc for GetServerResponse
        """
        request = pb2.Message(message=message)
        return self.stub.GetServerResponse(request)
    

class BidirectionalClient:
    """
    Client for gRPC Bidirectional functionality
    """

    def __init__(self, host, secure=False, port=50051):
        self.host = host
        self.server_port = port
        self.channel = self.channel = self._set_up_channel(secure)
        self.stub = pb2_grpc_bidir.BidirectionalStub(self.channel)

    def _set_up_channel(self, secure=False):
        if secure:
            try:
                cert_path = "./certs/server.crt"

                # Load the trusted server certificate (CA certificate)
                with open(cert_path, 'rb') as f:
                    trusted_certs = f.read()
            
                # Create SSL credentials
                credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)

                # Create a secure channel
                return grpc.secure_channel(f'{self.host}:{self.server_port}', credentials)

            except FileNotFoundError:
                print(f"The file {cert_path} was not found.")
            except PermissionError:
                print(f"You do not have permission to read {cert_path}.")
            except OSError as e:
                print(f"An unexpected OS error occurred: {e}")

        else:
            return grpc.insecure_channel(f'{self.host}:{self.server_port}')

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
            #print("Hello Server Sending you the %s" % msg.message)
            logger.log(f"Hello Server, sending you the {msg.message}\n", color=Fore.YELLOW)
            yield msg

    def make_message(self, message):
        return bidir.Message(
            message=message
        )


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
                        client = UnaryClient(target, args.secure)
                        response = client.get_url(message)
                        logger.log(f"Response from {target}: {response}", color=Fore.GREEN)
                    elif args.type == "bidirectional":
                        client = BidirectionalClient(target, args.secure)
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
