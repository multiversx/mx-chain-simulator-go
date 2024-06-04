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

#### Response Body
```json
{
  "data": {},
  "error": "",
  "code": "successful"
}
```

### `POST /simulator/generate-blocks-until-epoch-reached/:epoch`

This endpoint initiates the generation of blocks for each shard until the target epoch is reached.

##### Request
- **Method:** POST
- **Path:** `/simulator/generate-blocks-until-epoch-reached/:epoch`
- **Parameters:**
  - `epoch` (path parameter): The target epoch to be reached.

##### Response
- **Status Codes:**
  - `200 OK`: Blocks generated successfully, target epoch reached.
  - `400 Bad Request`: Invalid request parameters.

#### Response Body
```json
{
  "data": {},
  "error": "",
  "code": "successful"
}
```

### `POST /simulator/force-epoch-change`

This endpoint will trigger the chain to move in the next epoch. (this endpoint will generate a few blocks till next epoch is reached)

##### Request
- **Method:** POST
- **Path:** `/simulator/force-epoch-change`

##### Response
- **Status Codes:**
  - `200 OK`: Next epoch reached.
  - `400 Bad Request`: Invalid request parameters.

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

### `GET /simulator/observers`

This endpoint returns information about the observers that are behind chain simulator

##### Request
- **Method:** GET
- **Path:** `/simulator/observers`

##### Response
- **Status Codes:**
  - `200 OK`: Observers information retrieved successfully.

#### Response Body (Example)
```
{
  "data": {
    "0": {
       "api-port": 52747
    },
    "1": {
       "api-port": 52749
    }
     // ... additional observers entries
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

This endpoint allows you to set the entire state for a provided list of addresses. Additionally, this endpoint
will generate one block per shard to apply the address state, unless specified otherwise.

##### Request
- **Method:** POST
- **Path:** `/simulator/set-state`
- **URL parameter** `noGenerate` 

##### URL Parameter: `noGenerate`
- **Description:**
  - **Type:** Boolean
  - **Optional:** Yes
  - **Default:** `false`
  - **Behavior:** Setting the noGenerate=true is useful when multiple calls to this
  endpoint are required and the calls should be executed as fast as possible. In this case,
  to reflect the state changes, the user should manually call the generate-blocks endpoint
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


### `POST /simulator/set-state-overwrite`

This endpoint allows you to set the entire state (also will clean the old state of the provided accounts) for a provided list of addresses.

##### Request
- **Method:** POST
- **Path:** `/simulator/set-state`
- **URL parameter** `noGenerate`
- 
##### URL Parameter: `noGenerate`
- **Description:**
  - **Type:** Boolean
  - **Optional:** Yes
  - **Default:** `false`
  - **Behavior:** Setting the noGenerate=true is useful when multiple calls to this endpoint are required and the calls
  should be executed as fast as possible. In this case, to reflect the state changes, 
  the user should manually call the generate-blocks endpoint

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


### `POST /simulator/add-keys`

This endpoint allows you to add new validator private keys in the multi key handler.

##### Request
- **Method:** POST
- **Path:** `/simulator/add-keys`


##### Request Body
The request body should be a JSON object representing an object with the next format.

Example:
```
{
  "privateKeysBase64":[
    "ZjVkYjgwZDE1NzE5MDJiN2UzMDNlNDIzOTUzZGU2NTQ4NzBiYzM1MDhmMThkNGRhODgzODk1NTI3ZjcyMjYxYw==",
    "ZTVhYTU0NjI0ZmRjNDZkMDdmNDU5ZGZiZDFmNmUxYWZlMTRmN2YyOTY1ZTJiMGJhZjBmMGE0MGQ3ZjYwNDYxYg==",
  ]
}
```


##### Response
- **Status Codes:**
  - `200 OK`: Validator keys were added successfully.
  - `404 Bad Request`: Invalid request parameters.

#### Response Body
```json
{
  "data": {},
  "error": "",
  "code": "successful"
}
```

### `POST /simulator/force-reset-validator-statistics`

This endpoint resets (clears) an internal cache used by the `/validator/statistics` API endpoint route.

##### Request
- **Method:** POST
- **Path:** `/simulator/force-reset-validator-statistics`

##### Response
- **Status Codes:**
  - `200 OK`: Cache cleared successfully.
  - `400 Bad Request`: Internal error while clearing the cache.

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
        # initial-round specifies with what round the chain simulator will start
        initial-round = 0
        # initial-nonce specifies with what nonce the chain simulator will start
        initial-nonce = 0
        # initial-epoch specifies with what epoch the chain simulator will start
        initial-epoch = 0
        # mx-chain-go-repo will be used to fetch the node configs folder
        mx-chain-go-repo = "https://github.com/multiversx/mx-chain-go"
        # mx-chain-proxy-go-repo will be used to fetch the proxy configs folder
        mx-chain-proxy-go-repo = "https://github.com/multiversx/mx-chain-proxy-go"
    [config.logs]
        log-file-life-span-in-mb = 1024 # 1GB
        log-file-life-span-in-sec = 432000 # 5 days
        log-file-prefix = "chain-simulator"
        logs-path = "logs"
    [config.blocks-generator]
        # auto-generate-blocks specifies if the chain simulator should auto generate blocks
        auto-generate-blocks = false
        # block-time-in-milliseconds specifies the time between blocks generation in case auto-generate-blocks is enabled
        block-time-in-milliseconds = 6000
```

There is also an optional configuration file called `nodeOverride.toml` that can be used to alter specific configuration options 
for the nodes that assemble the chain simulator. The override mechanism is the same as the one found on the mx-chain-go, prefs.toml file.
In this tool, the flag option called `--node-override-config` can load more than one override toml file by specifying the paths separated 
by the `,` character. Example: `--node-override-config ./config/override1.toml,./config/override2.toml`. The default 
`./config/nodeOverrideDefault.toml` file is added automatically.

The **_[nodeOverride.toml](./cmd/chainsimulator/config/config.toml)_** file:

```toml 
# OverridableConfigTomlValues represents an array of items to be overloaded inside other configuration files, which can be helpful
# so that certain config values need to remain the same during upgrades.
# (for example, an Elasticsearch user wants external.toml->ElasticSearchConnector.Enabled to remain true all the time during upgrades, while the default
# configuration of the node has the false value)
# The Path indicates what value to change, while Value represents the new value in string format. The node operator must make sure
# to follow the same type of the original value (ex: uint32: "37", float32: "37.0", bool: "true")
# File represents the file name that holds the configuration. Currently, the supported files are:
# api.toml, config.toml, economics.toml, enableEpochs.toml, enableRounds.toml, external.toml, fullArchiveP2P.toml, p2p.toml, ratings.toml, systemSmartContractsConfig.toml
# -------------------------------
# Un-comment and update the following section in order to enable config values overloading
# -------------------------------
# OverridableConfigTomlValues = [
#    { File = "config.toml", Path = "StoragePruning.NumEpochsToKeep", Value = "4" },
#    { File = "config.toml", Path = "MiniBlocksStorage.Cache.Name", Value = "MiniBlocksStorage" },
#    { File = "external.toml", Path = "ElasticSearchConnector.Enabled", Value = "true" }
#]
```

**Note:** If the port for the proxy server is set to 0, a random free port will be selected. 
The URL for the proxy is printed in the logs in a line that looks like:
```
INFO [2024-04-18 10:48:47.231]   chain simulator's is accessible through the URL localhost:38099 
```


### Build docker image
```
DOCKER_BUILDKIT=1 docker build -t chainsimulator:latest .
```

### Run with docker
```
docker run -p 8085:8085 chainsimulator:latest --log-level *:DEBUG
```

### Enable `HostDriver`
  
To enable the host driver in the chain simulator, follow these steps:

1. If you're using the chain simulator for the first time, initiate it once to retrieve
   the node and proxy configuration from GitHub.
2. Open the file located at `cmd/chainsimulator/config/node/config/external.toml`.
   Enable the host driver and modify the configuration.
   Ensure that the parameters AcknowledgeTimeoutInSec and RetryDurationInSec are set to a value of 1.

## Contribution

Contributions to the mx-chain-simulator-go module are welcomed. Whether you're interested in improving its features, 
extending its capabilities, or addressing issues, your contributions can help the 
community make the module even more robust.
