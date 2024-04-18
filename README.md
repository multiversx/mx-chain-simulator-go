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
```
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


### `POST /simulator/address/:address/set-state`

This endpoint allows you to set the state at a specific address.

##### Request
- **Method:** POST
- **Path:** `/simulator/address/:address/set-state`
- **Parameters:**
    - `address` (path parameter): The address for which the state will be set.

##### Request Body
The request body should be a JSON object representing a map of hex-encoded key-value pairs.

Example:
```
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


### `POST /simulator/set-state`

This endpoint allows you to set the entire state for a provided list of addresses.

##### Request
- **Method:** POST
- **Path:** `/simulator/set-state`


##### Request Body
The request body should be a JSON object representing an array of object with the next format.

Example:
```
[
	{
		"address": "erd1qqqqqqqqqqqqqpgqmzzm05jeav6d5qvna0q2pmcllelkz8xddz3syjszx5",
		"balance": "431271308732096033771131",
		"code": "0061736d010000000129086000006000017f60027f7f017f60027f7f0060017f0060037f7f7f017f60037f7f7f0060017f017f0290020b03656e7619626967496e74476574556e7369676e6564417267756d656e74000303656e760f6765744e756d417267756d656e7473000103656e760b7369676e616c4572726f72000303656e76126d42756666657253746f726167654c6f6164000203656e76176d427566666572546f426967496e74556e7369676e6564000203656e76196d42756666657246726f6d426967496e74556e7369676e6564000203656e76136d42756666657253746f7261676553746f7265000203656e760f6d4275666665725365744279746573000503656e760e636865636b4e6f5061796d656e74000003656e7614626967496e7446696e697368556e7369676e6564000403656e7609626967496e744164640006030b0a010104070301000000000503010003060f027f0041a080080b7f0041a080080b074607066d656d6f7279020004696e697400110667657453756d00120361646400130863616c6c4261636b00140a5f5f646174615f656e6403000b5f5f686561705f6261736503010aca010a0e01017f4100100c2200100020000b1901017f419c8008419c800828020041016b220036020020000b1400100120004604400f0b4180800841191002000b16002000100c220010031a2000100c220010041a20000b1401017f100c2202200110051a2000200210061a0b1301017f100c220041998008410310071a20000b1401017f10084101100d100b210010102000100f0b0e0010084100100d1010100e10090b2201037f10084101100d100b210110102202100e220020002001100a20022000100f0b0300010b0b2f0200418080080b1c77726f6e67206e756d626572206f6620617267756d656e747373756d00419c80080b049cffffff",
		"rootHash": "76cr5Jhn6HmBcDUMIzikEpqFgZxIrOzgNkTHNatXzC4=",
		"codeMetadata": "BQY=",
		"codeHash": "n9EviPlHS6EV+3Xp0YqP28T0IUfeAFRFBIRC1Jw6pyU=",
		"developerReward": "5401004999998",
		"ownerAddress": "erd1ss6u80ruas2phpmr82r42xnkd6rxy40g9jl69frppl4qez9w2jpsqj8x97",
		"keys": {
			"73756d": "0a"
		}
	},
	{
		"address": "erd1ss6u80ruas2phpmr82r42xnkd6rxy40g9jl69frppl4qez9w2jpsqj8x97",
		"balance": "431271308732096033771131"
	}
	// ...additional state for another address
]
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


---


## Prerequisites

Before proceeding, ensure you have the following prerequisites:

- Go programming environment set up.
- Git installed.


## Install

Using the `cmd/chainsimulator` package as root, execute the following commands:

- install go dependencies: `go install`
- build executable: `go build -o chainsimulator`

Note: go version 1.20.* should be used to build the executable. Using version 1.21.* leads to build failures currently.


## Launching the chainsimulator

CLI: run `--help` to get the command line parameters

```
./chainsimulator --help
```

Before launching the `chainsimulator` service, it has to be configured so that it runs with the correct configuration.

The **_[config.toml](./cmd/chainsimulator/config/config.toml)_** file: 

```toml
[config]
    [config.simulator]
        # server-port paramter specifies the port of the http server that the proxy component will respond on
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

**Note:** If the port for the proxy server is set to 0, a random free port will be selected. The URL for the proxy 
is printed in the logs in a line that looks like:
```
INFO [2024-04-18 10:48:47.231]   chain simulator's is accessible through the URL localhost:38099 
```


## Contribution

Contributions to the mx-chain-simulator-go module are welcomed. Whether you're interested in improving its features, 
extending its capabilities, or addressing issues, your contributions can help the 
community make the module even more robust.
