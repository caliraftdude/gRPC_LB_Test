import grpc
import socket
import argparse
from concurrent import futures
from colorama import Fore

from logger import ColorLogger
from config import ServerConfig
from grpc_api import pb2, pb2_grpc, pb2_grpc_bidir

# Get Logging
logger = ColorLogger("gRPC Server")


class BidirectionalService(pb2_grpc_bidir.BidirectionalServicer):

    def GetServerResponse(self, request_iterator, context):
        for message in request_iterator:
            yield message

class UnaryService(pb2_grpc.UnaryServicer):

    def __init__(self, *args, **kwargs):
        pass

    def GetServerResponse(self, request, context):

        # get the string from the incoming request, and svr identity
        message = request.message
        hostname, peer_ip = get_server_identity(context)

        # create the response message
        result = f"Hello from {hostname} at {peer_ip}!  Received your message: {message}"
        result = {'message': result, 'received': True}

        # Print to console
        logger.log(f"Processed request from {peer_ip} on {hostname}: {message}", color=Fore.GREEN)

        # Send it
        return pb2.MessageResponse(**result)
    

def get_server_identity(request_context):
    hostname = socket.gethostname()
    peer_info = request_context.peer()  # e.g., 'ipv4:127.0.0.1:12345'
    server_ip = peer_info.split(":")[1] if "ipv4" in peer_info else "unknown" # Extract IP from gRPC peer string
    return hostname, server_ip


def main():
    
    sc = ServerConfig( argparse.ArgumentParser(description="gRPC Server"), logger )
    ip, port, service_type = sc.get_args()

    # Setup server and thread pool
    if service_type == "unary":
        logger.info("Starting Unary gRPC Server...")
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        pb2_grpc.add_UnaryServicer_to_server(UnaryService(), server)

    elif service_type == "bidirectional":
        logger.info("Starting Bidirectional gRPC Server...")
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        pb2_grpc_bidir.add_BidirectionalServicer_to_server(BidirectionalService(), server)

    else:
        raise ValueError("Invalid service type. Choose 'unary' or 'bidirectional'.")

    # Bind to address and port - use env vars, cmd args or defaults
    if sc.args.secure:
        try:
            cert_path = "./certs/server.crt"
            key_path = "./certs/server.key" 
            
            # Load server private key and certificate
            with open(key_path, 'rb') as f:
                private_key = f.read()
            with open(cert_path, 'rb') as f:
                certificate_chain = f.read()    

            # Create server credentials
            server_credentials = grpc.ssl_server_credentials(private_key_certificate_chain_pairs=[(private_key, certificate_chain)] )

            # Create a secure server
            server.add_secure_port(f"{ip}:{port}", server_credentials)
            logger.info(f"Created secure server on {ip}:{port}...")

        except FileNotFoundError:
            logger.error(f"The file {cert_path} was not found.")
        except PermissionError:
            logger.error(f"You do not have permission to read {cert_path}.")
        except OSError as e:
            logger.error(f"An unexpected OS error occurred: {e}")
        
    else:
        server.add_insecure_port(f"{ip}:{port}")
        logger.info(f"Created insecure server on {ip}:{port}...")
 
    # Start the server
    server.start()
    logger.info("Server started. Listening for requests...")

    # Keep the server running unless ctrl-c is pressed
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Server shutting down...")


if __name__ == '__main__':
    main()


