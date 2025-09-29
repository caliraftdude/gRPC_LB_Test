import sys
import grpc
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


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <host1> [<host2> ...]")
        sys.exit(1)

    message = "Hello Server you there?"
    hosts = sys.argv[1:]

    for host in hosts:
        print(f"\nTrying to connect to {host}...")
        try:
            client = UnaryClient(host)
            response = client.get_url(message)
            print(f"Response from {host}: {response}")
        except Exception as e:
            print(f"Failed to connect to {host}: {e}")


if __name__ == '__main__':
    main()

