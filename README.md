# AlgoHood Utilities

A collection of common utilities for developing algorithmic trading modules.

## Features

- **Async QUIC Communication**
  - QUIC client/server implementation with message chunk handling
  - Connection management with keep-alive
  - Pub/Sub pattern support

- **Redis Integration**
  - Async Redis client with time-series support
  - String/hash/set/list operations
  - Data sharding capabilities

- **ZeroMQ Utilities**
  - Async REQ/ROUTER/PUB/SUB patterns
  - Message routing and subscription management

- **Time Series Processing**
  - InfluxDB client integration
  - Data point batch operations
  - Time-range queries with filters

- **Date/Time Utilities**
  - Timestamp conversions (local/UTC)
  - Date range generation
  - Microsecond precision handling

- **Logging System**
  - Rotating file handlers
  - Multi-level logging (DEBUG/INFO/ERROR)
  - Online/offline logging modes

- **Trading Infrastructure**
  - Order management base classes
  - Risk management interfaces
  - Signal generation abstractions
  - Performance tracking framework

## Installation

This package is a dependency of `algohood_strategy` and will be automatically installed when you install the main package:

## Requirements

Python 3.10+ with dependencies listed in `pyproject.toml`

## Contributing

Contributions welcome! Please follow:
1. Fork the repository
2. Create your feature branch
3. Submit a pull request

## License

Proprietary License (Contact AlgoHood for licensing details)
