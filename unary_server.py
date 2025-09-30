import grpc
import os
import argparse
import socket
from concurrent import futures

import time

import unary_pb2_grpc as pb2_grpc
import unary_pb2 as pb2


class UnaryService(pb2_grpc.UnaryServicer):

    def __init__(self, *args, **kwargs):
        pass

    def GetServerResponse(self, request, context):

        # get the string from the incoming request, and svr identity
        message = request.message
        hostname, peer_ip = get_server_identity(context)

        # create the response message
        message = f"Hello from {hostname} at {peer_ip}!\nreceived your message: {message}"
        result = {'message': result, 'received': True}

        # Print to console
        print(f"Processed request from {peer_ip} on {hostname}: {message}")

        # Send it
        return pb2.MessageResponse(**result)
    

def get_server_identity(request_context):
    hostname = socket.gethostname()
    peer_info = request_context.peer()  # e.g., 'ipv4:127.0.0.1:12345'
    server_ip = peer_info.split(":")[1] if "ipv4" in peer_info else "unknown" # Extract IP from gRPC peer string
    return hostname, server_ip


def get_server_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, help="IP address to bind to")
    parser.add_argument("--port", type=int, help="Port to bind to")
    args = parser.parse_args()

    ip = args.ip or os.getenv("GRPC_SERVER_IP", "0.0.0.0")
    port = args.port or int(os.getenv("GRPC_SERVER_PORT", "50051"))

    return ip, port


def serve():
    # Setup server and thread pool
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_UnaryServicer_to_server(UnaryService(), server)

    # Bind to address and port - use env vars, cmd args or defaults
    ip, port = get_server_config()
    server.add_insecure_port(f"{ip}:{port}")
 
    # Start the server
    server.start()
    print("Server started. Listening for requests...")

    # Keep the server running unless ctrl-c is pressed
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Server shutting down...")



if __name__ == '__main__':
    serve()
