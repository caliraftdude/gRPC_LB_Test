# Setup of environment
- sudo apt update
- sudo apt upgrade -y
- sudo apt install python3-pip -y
- sudo apt install python3-virtualenv -y

- virtualenv -p python3 .env
- source .env/bin/activate
- pip install grpcio grpcio-tools

# code generation
- Write the proto file and then run:
- python -m grpc_tools.protoc --proto_path=. ./unary.proto --python_out=. --grpc_python_out=.

# Server setup:
- ensure venv is setup and tools/libraries are installed
- You can use environment variables to control the ip address and port that the server listens on:
-- GRPC_SERVER_IP (default is 0.0.0.0 or all ip addresses)
-- GRPC_SERVER_PORT (default is 50051)
- You can also override defaults and environment variables using the command line arguments:
-- --ip - IP address to bind to
-- --port - Port to bind to

# Client 
- Client accepts 1..n ip addresses and will attempt to communicate with each of them
