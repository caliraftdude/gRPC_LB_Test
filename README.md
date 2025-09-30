# Setup of environment
- sudo apt update
- sudo apt upgrade -y
- sudo apt install python3-pip -y
- sudo apt install python3-virtualenv -y

- virtualenv -p python3 .env
- source .env/bin/activate
- pip install grpcio grpcio-tools

- Write the proto file and then run:
- python -m grpc_tools.protoc --proto_path=. ./unary.proto --python_out=. --grpc_python_out=.


