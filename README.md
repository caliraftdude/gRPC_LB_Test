# grpc test client / server

## Setup of environment
- sudo apt update
- sudo apt upgrade -y
- sudo apt install python3-pip -y
- sudo apt install python3-virtualenv -y

- virtualenv -p python3 .env
- source .env/bin/activate
- pip install grpcio grpcio-tools

## code generation
- Write the proto file and then run:
- python -m grpc_tools.protoc --proto_path=. ./unary.proto --python_out=. --grpc_python_out=.

## Server setup:
1. ensure venv is setup and tools/libraries are installed
2. You can use environment variables to control the ip address and port that the server listens on:
    1. GRPC_SERVER_IP (default is 0.0.0.0 or all ip addresses)
    2. GRPC_SERVER_PORT (default is 50051)
    3. GRPC_SERVICE_TYPE ["unary", "bidirectional"] (default is unary)
3. You can also override defaults and environment variables using the command line arguments:
    1. --ip - IP address to bind to
    2. --port - Port to bind to
    3. --type" - ["unary", "bidirectional"]

## Client 
- Client accepts 1..n ip addresses and will attempt to communicate with each of them

### references
1. https://www.velotio.com/engineering-blog/grpc-implementation-using-python
