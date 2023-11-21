# mx-chain-simulator-go

## Overview

`mx-chain-simulator-go` is a binary that provides all the [mx-chain-proxy-go](https://github.com/multiversx/mx-chain-proxy-go) endpoints 
and includes additional endpoints for specific operations. 

This simulator is designed to replicate the behavior of a local testnet. Unlike a traditional testnet,
this simulator operates without a consensus group, allowing for isolated testing and development.

By operating without a consensus group, the simulator accelerates block generation, enabling swift system testing of smart contracts. 
Blocks are promptly generated through a dedicated endpoint whenever users initiate the call, resulting in a more efficient testing environment.


## Features

- Implements all `mx-chain-proxy-go` endpoints.
- Extra endpoints for specific operations.
- Simulates the behavior of a local testnet without a consensus group.


## API Documentation

`mx-chain-simulator-go` includes all the [proxy endpoints](https://github.com/multiversx/mx-chain-proxy-go#rest-api-endpoints)


### Additionally, the simulator offers custom endpoints:

### `POST /simulator/generate-blocks/:num`

This endpoint initiates the generation of a specified number of blocks for each shard.

##### Request
- **Method:** POST
- **Path:** `/simulator/generate-blocks/:num`
- **Parameters:**
    - `num` (path parameter): The number of blocks to generate for each shard.

##### Response
- **Status Codes:**
    - `200 OK`: Blocks generated successfully.
    - `400 Bad Request`: Invalid request parameters.
    - 
#### Response Body
```json
{
  "data": {},
  "error": "",
  "code": "successful"
}
```

### `GET /simulator/initial-wallets`

This endpoint returns the initial wallets (address and private key hex encoded).

##### Request
- **Method:** GET
- **Path:** `/simulator/initial-wallets`

##### Response
- **Status Codes:**
    - `200 OK`: Initial wallets retrieved successfully.

#### Response Body (Example)
```json
{
  "data": {
    "initialWalletWithStake": {
      "address": "erd18e5tqg3x2fvh2f3g2747639erk...",
      "privateKeyHex": "7ce93f48840c4a67fdcdc97c..."
    },
    "shardWallets": {
      "0": {
        "address": "erd1844ch276gqfmhjgj8jjca4akpf...",
        "privateKeyHex": "2024e8a0f202ae3536d336c3..."
      },
      // ... additional wallet entries
    }
  },
  "error": "",
  "code": "successful"
}
```


### `POST /simulator/:address/set-state`

This endpoint allows you to set the state at a specific address.

##### Request
- **Method:** POST
- **Path:** `/simulator/:address/set-state`
- **Parameters:**
    - `address` (path parameter): The address for which the state will be set.

##### Request Body
The request body should be a JSON object representing a map of hex-encoded key-value pairs.

Example:
```json
{
  "keyHex1": "valueHex1",
  "keyHex2": "valueHex2",
  // ... additional hex-encoded key-value pairs
}
```


##### Response
- **Status Codes:**
    - `200 OK`: State set successfully.
    - `404 Bad Request`: Invalid request parameters.

#### Response Body
```json
{
  "data": {},
  "error": "",
  "code": "successful"
}
```


---


## Prerequisites

Before proceeding, ensure you have the following prerequisites:

- Go programming environment set up.
- Git installed.


## Install

Using the `cmd/chainsimulator` package as root, execute the following commands:

- install go dependencies: `go install`
- build executable: `go build -o chainsimulator`


## Launching the chainsimulator

CLI: run `--help` to get the command line parameters

```
./chainsimulator --help
```

Before launching the chainsimulator service, it has to be configured so that it runs with the correct configuration.

The **_[config.toml](./cmd/chainsimulator/config/config.toml)_** file: 

```toml
[config]
    [config.simulator]
        # server-port paramter specifies the port of the http server
        server-port = 8085
        # num-of-shards parameter specifies the number of shard that chain simulator will simulate
        num-of-shards = 3
        # round-duration-in-milliseconds parameter specifies the duration of a simulated round. The timestamp between two headers will correspond to the round duration but will not reflect real-time
        round-duration-in-milliseconds = 6000
        # rounds-per-epoch specifies the number of rounds per epoch
        rounds-per-epoch = 20
        # mx-chain-go-repo will be used to fetch the node configs folder
        mx-chain-go-repo = "https://github.com/multiversx/mx-chain-go"
        # mx-chain-proxy-go-repo will be used to fetch the proxy configs folder
        mx-chain-proxy-go-repo = "https://github.com/multiversx/mx-chain-proxy-go"
    [config.logs]
        log-file-life-span-in-mb = 1024 # 1GB
        log-file-life-span-in-sec = 432000 # 5 days
        log-file-prefix = "chain-simulator"
        logs-path = "logs"
```


## Contribution

Contributions to the mx-chain-es-indexer-go module are welcomed. Whether you're interested in improving its features, 
extending its capabilities, or addressing issues, your contributions can help the 
community make the module even more robust.
