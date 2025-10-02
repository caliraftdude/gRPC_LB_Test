# gRPC Load Balancer Test Framework

## Introduction / About

The gRPC Load Balancer Test Framework is a comprehensive testing suite designed to evaluate and validate Big-IP gRPC proxy configurations. This project provides both client and server implementations that support multiple gRPC communication patterns, enabling thorough testing of load balancing, failover, and proxy behavior in distributed environments.

### Key Features
- **Dual Communication Modes**: Supports both unary (request/response) and bidirectional streaming gRPC patterns
- **Multi-Target Testing**: Client can connect to multiple server instances sequentially or repeatedly
- **Security Support**: Built-in SSL/TLS support for secure channel testing
- **Flexible Configuration**: Environment variables, command-line arguments, and default values
- **Rich Logging**: Color-coded console output for easy debugging and monitoring
- **Load Testing Capabilities**: Configurable delays, iterations, and random timing patterns

### Use Cases
- Validating Big-IP gRPC proxy configurations
- Testing load balancing algorithms and distribution
- Evaluating failover scenarios
- Performance benchmarking of gRPC services
- SSL/TLS certificate validation in proxy environments

## Installation and Dependencies

### Prerequisites
- Python 3.7 or higher
- pip package manager
- virtualenv (recommended for isolated environments)

### System Setup
```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install Python and pip
sudo apt install python3-pip -y
sudo apt install python3-virtualenv -y
```

### Project Installation
```bash
# Clone the repository
git clone <repository-url>
cd gRPC_LB_Test

# Create and activate virtual environment
virtualenv -p python3 .env
source .env/bin/activate

# Install required packages
pip install grpcio grpcio-tools colorama
```

### Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| grpcio | Latest | Core gRPC library for Python |
| grpcio-tools | Latest | Protocol buffer compiler and tools |
| colorama | Latest | Cross-platform colored terminal output |

### Generating Protocol Buffer Files
If you modify the .proto files, regenerate the Python bindings:
```bash
# For unary service
python -m grpc_tools.protoc --proto_path=./grpc_api ./grpc_api/unary.proto \
    --python_out=./grpc_api --grpc_python_out=./grpc_api

# For bidirectional service
python -m grpc_tools.protoc --proto_path=./grpc_api ./grpc_api/bidirectional.proto \
    --python_out=./grpc_api --grpc_python_out=./grpc_api
```

## Running the Client and Server

### Server Configuration

#### Command Line Arguments
| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--type` | string | unary | Service type: 'unary' or 'bidirectional' |
| `--ip` | string | 0.0.0.0 | IP address to bind the server to |
| `--port` | int | 50051 | Port number for the server |
| `--secure` | flag | False | Enable SSL/TLS secure channel |

#### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `GRPC_SERVER_IP` | 0.0.0.0 | Server bind IP address |
| `GRPC_SERVER_PORT` | 50051 | Server port number |
| `GRPC_SERVICE_TYPE` | unary | Service type (unary/bidirectional) |
| `GRPC_CERT_PATH` | ./certs/server.crt | Path to SSL certificate |
| `GRPC_KEY_PATH` | ./certs/server.key | Path to SSL private key |

#### Server Examples
```bash
# Start unary server on default settings
python server.py

# Start bidirectional server on custom port
python server.py --type bidirectional --port 50052

# Start secure unary server
python server.py --secure --ip 192.168.1.100 --port 50051

# Using environment variables
export GRPC_SERVER_PORT=50053
export GRPC_SERVICE_TYPE=bidirectional
python server.py
```

### Client Configuration

#### Command Line Arguments
| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--targets` | string | Yes | - | Comma-separated list of server addresses |
| `--type` | string | No | unary | Service type: 'unary' or 'bidirectional' |
| `--port` | int | No | 50051 | Default port for targets |
| `--secure` | flag | No | False | Use SSL/TLS secure channel |
| `--repeat` | int | No | 1 | Number of iterations (0 for infinite) |
| `--delay-mode` | string | No | fixed | Delay mode: 'fixed' or 'random' |
| `--delay` | float | No | 1.0 | Fixed delay in seconds |
| `--random-min` | float | No | 0.5 | Minimum random delay |
| `--random-max` | float | No | 2.0 | Maximum random delay |

#### Client Examples
```bash
# Connect to single server
python client.py --targets localhost

# Connect to multiple servers
python client.py --targets "grpcsvr-1,grpcsvr-2,grpcsvr-3" --port 50051

# Bidirectional streaming with custom delays
python client.py --type bidirectional --targets localhost \
    --delay-mode random --random-min 1 --random-max 5

# Continuous testing with infinite loop
python client.py --targets "lb.example.com" --repeat 0 --delay 2

# Secure connection
python client.py --targets localhost --secure
```

## How the gRPC Services Work

### Unary Service

The unary service implements a simple request-response pattern where the client sends a single message and receives a single response.

#### Message Flow
```
┌──────────┐          ┌──────────┐          ┌──────────┐
│  Client  │          │  Big-IP  │          │  Server  │
└────┬─────┘          └────┬─────┘          └────┬─────┘
     │                      │                      │
     │   Message Request    │                      │
     ├─────────────────────►│                      │
     │                      │   Forward Request    │
     │                      ├─────────────────────►│
     │                      │                      │
     │                      │                      ├─┐ Process
     │                      │                      │ │ Request
     │                      │                      │◄┘
     │                      │   MessageResponse    │
     │                      │◄─────────────────────┤
     │   Forward Response   │                      │
     │◄─────────────────────┤                      │
     │                      │                      │
     └──────────────────────┴──────────────────────┘
```

#### Protocol Details
- **Request Message**: Contains a simple string message
- **Response Message**: Contains the processed message and a received flag
- **Server Processing**: Adds server identity (hostname and IP) to response

### Bidirectional Service

The bidirectional service implements a streaming pattern where both client and server can send multiple messages in both directions simultaneously.

#### Message Flow
```
┌──────────┐          ┌──────────┐          ┌──────────┐
│  Client  │          │  Big-IP  │          │  Server  │
└────┬─────┘          └────┬─────┘          └────┬─────┘
     │                      │                      │
     │◄═══════ Stream Established ════════════════►│
     │                      │                      │
     ├──── Message 1 ──────►├─────────────────────►│
     ├──── Message 2 ──────►├─────────────────────►│
     │                      │                      │
     │◄─────────────────────┤◄──── Response 1 ────┤
     │◄─────────────────────┤◄──── Response 2 ────┤
     │                      │                      │
     ├──── Message 3 ──────►├─────────────────────►│
     │◄─────────────────────┤◄──── Response 3 ────┤
     │                      │                      │
     │    (Continues...)    │                      │
     │                      │                      │
     │◄═══════ Stream Closed ═════════════════════►│
     └──────────────────────┴──────────────────────┘
```

#### Protocol Details
- **Streaming Messages**: Both sides can send messages at any time
- **Echo Pattern**: Server echoes back each received message
- **Connection Persistence**: Stream remains open for multiple exchanges

## Detailed Code Description

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     gRPC_LB_Test Framework                   │
├───────────────────────────┬─────────────────────────────────┤
│         Client            │            Server                │
├───────────────────────────┼─────────────────────────────────┤
│                           │                                  │
│  ┌──────────────────┐     │     ┌──────────────────┐        │
│  │   BaseClient     │     │     │  UnaryService    │        │
│  └────────┬─────────┘     │     └──────────────────┘        │
│           │                │                                  │
│  ┌────────▼─────────┐     │     ┌──────────────────┐        │
│  │   UnaryClient    │     │     │ BidirectionalSvc │        │
│  └──────────────────┘     │     └──────────────────┘        │
│                           │                                  │
│  ┌──────────────────┐     │     ┌──────────────────┐        │
│  │BidirectionalClient│    │     │   gRPC Server    │        │
│  └──────────────────┘     │     └──────────────────┘        │
│                           │                                  │
├───────────────────────────┴─────────────────────────────────┤
│                     Shared Components                        │
├───────────────────────────────────────────────────────────  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Config  │  │  Logger  │  │   Proto  │  │   Certs  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

#### Configuration Management (config.py)

```
┌─────────────────────────────────┐
│         BaseConfig              │
│  - Common argument parsing      │
│  - Service type selection       │
│  - Security settings            │
└────────────┬────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼──────┐    ┌────▼──────┐
│ServerConfig│  │ClientConfig│
│           │   │            │
│ - IP/Port │   │ - Targets  │
│ - Binding │   │ - Delays   │
│ - Service │   │ - Repeats  │
└───────────┘   └────────────┘
```

| Class | Responsibility | Key Methods |
|-------|---------------|-------------|
| BaseConfig | Common configuration parsing | parse_cmd_args(), get_args() |
| ServerConfig | Server-specific settings | Inherits base + IP/port config |
| ClientConfig | Client-specific settings | Target validation, delay config |

#### Client Flow Diagram

```
Start
  │
  ▼
Parse Arguments
  │
  ▼
Split Targets ──────┐
  │                 │
  ▼                 │
┌─────────────┐     │
│  Iteration  │◄────┘
│    Loop     │
└──────┬──────┘
       │
  ┌────▼────┐
  │For Each │
  │ Target  │
  └────┬────┘
       │
  ┌────▼─────────┐
  │Select Service│
  │    Type      │
  └───┬──────┬───┘
      │      │
   Unary  Bidirectional
      │      │
  ┌───▼──┐ ┌─▼──────────┐
  │Send  │ │Send Stream │
  │Msg   │ │Messages    │
  └───┬──┘ └─┬──────────┘
      │      │
  ┌───▼──┐ ┌─▼──────────┐
  │Get   │ │Get Stream  │
  │Reply │ │Responses   │
  └───┬──┘ └─┬──────────┘
      │      │
      └──┬───┘
         │
    ┌────▼────┐
    │  Delay  │
    └────┬────┘
         │
    ┌────▼────┐
    │  Check  │──No──┐
    │  Repeat │      │
    └────┬────┘      │
         │Yes        │
         └───────────┘
```

#### Server Processing Flow

```
┌──────────────┐
│Server Start  │
└──────┬───────┘
       │
   ┌───▼────┐
   │Service │
   │Select  │
   └──┬──┬──┘
      │  │
 Unary│  │Bidirectional
      │  │
  ┌───▼──▼───┐
  │Create    │
  │gRPC      │
  │Server    │
  └────┬─────┘
       │
  ┌────▼─────┐
  │Configure │
  │SSL/TLS   │
  └────┬─────┘
       │
  ┌────▼─────┐
  │Bind Port │
  └────┬─────┘
       │
  ┌────▼─────┐
  │  Listen  │
  │For Reqs  │
  └────┬─────┘
       │
  ┌────▼──────────┐
  │Process        │
  │Incoming       │◄─┐
  │Messages       │  │
  └────┬──────────┘  │
       │             │
  ┌────▼──────────┐  │
  │Send Response  ├──┘
  └───────────────┘
```

### Message Processing Details

| Component | Input | Processing | Output |
|-----------|-------|------------|--------|
| UnaryService | Message string | Add server identity | MessageResponse with hostname |
| BidirectionalService | Message stream | Echo each message | Message stream |
| UnaryClient | Target list | Send to each target | Collect responses |
| BidirectionalClient | Target | Send 5 messages | Receive echo stream |

## Areas for Improvement

### Current Limitations & Enhancement Opportunities

#### 1. **Advanced Testing Features**
- **Health Checks**: Implement gRPC health checking protocol
- **Metrics Collection**: Add Prometheus metrics for monitoring
- **Performance Benchmarking**: Built-in latency and throughput measurements
- **Connection Pooling**: Implement connection reuse for better performance

#### 2. **Protocol Enhancements**
- **Server Streaming**: Add server-to-client streaming pattern
- **Client Streaming**: Add client-to-server streaming pattern
- **Metadata Support**: Custom headers and trailers
- **Compression**: Enable gRPC compression algorithms
- **Interceptors**: Add request/response interceptors for debugging

#### 3. **Load Testing Capabilities**
```python
# Proposed enhancement structure
class LoadTestConfig:
    concurrent_clients: int
    requests_per_second: int
    test_duration: int
    ramp_up_time: int
    payload_sizes: List[int]
```

#### 4. **Resilience Testing**
- **Circuit Breaker**: Implement circuit breaker pattern
- **Retry Logic**: Configurable retry with backoff
- **Timeout Handling**: Per-request timeout configuration
- **Fault Injection**: Simulate network issues and failures

#### 5. **Configuration Management**
- **YAML/JSON Config Files**: External configuration files
- **Profile Support**: Named configuration profiles
- **Dynamic Reconfiguration**: Runtime parameter updates
- **Service Discovery**: Consul/etcd integration

#### 6. **Monitoring & Observability**
```yaml
# Proposed monitoring features
monitoring:
  - request_count
  - error_rate
  - latency_percentiles
  - connection_status
  - throughput_metrics
  - resource_usage
```

#### 7. **Security Enhancements**
- **mTLS Support**: Mutual TLS authentication
- **Token Authentication**: JWT/OAuth2 support
- **Certificate Rotation**: Automatic cert renewal
- **Security Scanning**: Built-in vulnerability checks

#### 8. **Testing Scenarios**
| Scenario | Description | Implementation |
|----------|-------------|----------------|
| Chaos Testing | Random failures | Fault injection framework |
| Load Balancing | Distribution testing | Multi-instance coordination |
| Failover | Automatic failover | Health check integration |
| Rate Limiting | Throttling tests | Request rate control |
| Stress Testing | Resource limits | Concurrent connection limits |

#### 9. **Reporting & Analysis**
- **HTML Reports**: Generate test result dashboards
- **CSV Export**: Export metrics for analysis
- **Real-time Dashboard**: WebSocket-based monitoring
- **Comparative Analysis**: Compare test runs

#### 10. **Developer Experience**
- **CLI Improvements**: Interactive mode, command completion
- **Docker Support**: Containerized deployment
- **Kubernetes Manifests**: K8s deployment configs
- **CI/CD Integration**: GitHub Actions/Jenkins pipelines

### Proposed Project Structure Enhancement
```
gRPC_LB_Test/
├── src/
│   ├── client/
│   │   ├── strategies/     # Different client strategies
│   │   ├── interceptors/   # Request/response interceptors
│   │   └── pools/          # Connection pooling
│   ├── server/
│   │   ├── services/       # Service implementations
│   │   ├── middleware/     # Server middleware
│   │   └── health/         # Health check service
│   ├── common/
│   │   ├── metrics/        # Metrics collection
│   │   ├── tracing/        # Distributed tracing
│   │   └── security/       # Security utilities
│   └── testing/
│       ├── scenarios/      # Test scenarios
│       ├── reports/        # Report generation
│       └── analysis/       # Result analysis
├── configs/                # Configuration files
├── deployments/           # Deployment manifests
├── docs/                  # Documentation
└── tests/                 # Unit tests
```

## Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

[Specify your license here]

## Support

For issues, questions, or suggestions, please:
- Open an issue on GitHub
- Contact the maintainers
- Check the documentation

---

*Last Updated: [Current Date]*
*Version: 1.0.0*

## Certificates and keying hotsheet
Generating a certificate with Subject Alternative Names (SANs) requires specifying extensions, which is impossible to do directly on the command line for a Certificate Signing Request (CSR). The recommended approach is to use a configuration file to define the SANs for the certificate. 
The steps below will guide you through creating a simple Certificate Authority (CA) and then issuing a server certificate with multiple SANs, all using separate, non-conflicting configuration files.

### Create a simple CA
- First, create a self-signed root CA certificate and its corresponding private key. This CA will be used to sign your server certificate later. 
#### Create the CA private key
Generate an RSA private key for the CA, encrypted with AES256 and protected by a strong passphrase. 
```console
openssl genrsa -aes256 -out ca.key 4096
```
Create the self-signed root CA certificate 
Use the private key to create a self-signed root certificate. The -x509 flag indicates that you are creating a self-signed certificate, not a CSR. 
sh
openssl req -new -x509 -sha256 -days 3650 -key ca.key -out ca.crt
You will be prompted to enter your passphrase and the CA's distinguished name (DN). For the "Common Name," enter a unique identifier for your CA, such as "My Root CA". 
Step 2: Create a server certificate with SANs 
Next, generate a private key and a Certificate Signing Request (CSR) for your server. Instead of modifying the main openssl.cnf file, you will create a temporary config file for the SANs. 
Create the server private key 
Generate an RSA private key for the server. For convenience, this example does not use a password (-nodes). 
sh
openssl genrsa -out server.key 4096
Create the SAN configuration file 
Create a text file named san.conf to specify the subject and the Subject Alternative Names. This file replaces the need to manually modify the system's openssl.cnf. 
san.conf
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = California
L = San Francisco
O = My Company
OU = My Department
CN = my.primary.com

[v3_req]
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = my.primary.com
DNS.2 = www.my.primary.com
DNS.3 = *.other.domain.com
IP.1 = 192.0.2.1
Create the server CSR 
Generate the CSR using the san.conf file you just created. 
sh
openssl req -new -key server.key -sha256 -out server.csr -config san.conf
Step 3: Sign the server certificate 
Finally, use your CA to sign the server's CSR. The extensions from san.conf will be included in the final certificate. 
sh
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 -sha256 -extfile san.conf -extensions v3_req
Step 4: Verify the certificate 
You can verify that the server certificate was correctly created with the SANs by printing its contents. 
sh
openssl x509 -in server.crt -text -noout
The output should include a section similar to this, confirming the SAN entries: 
X509v3 Subject Alternative Name: 
    DNS:my.primary.com, DNS:www.my.primary.com, DNS:*.other.domain.com, IP Address:192.0.2.1


### references
1. https://www.velotio.com/engineering-blog/grpc-implementation-using-python
