# mx-chain-simulator-go

## Overview

`mx-chain-simulator-go` is a binary that provides all the [mx-chain-proxy-go](https://github.com/multiversx/mx-chain-proxy-go) endpoints 
and includes additional endpoints for specific operations. 

This simulator is designed to replicate the behavior of a local testnet. Unlike a traditional testnet,
this simulator operates without a consensus group, allowing for isolated testing and development.

By operating without a consensus group, the simulator accelerates block generation, enabling swift system testing of smart contracts. 
Blocks are promptly generated through a dedicated endpoint whenever users initiate the call, resulting in a more efficient testing environment.


## Features

- Implements all mx-chain-proxy-go endpoints.
- Extra endpoints for specific operations.
- Simulates the behavior of a local testnet without a consensus group.


## Endpoints

`mx-chain-simulator-go` includes all the [proxy endpoints](https://github.com/multiversx/mx-chain-proxy-go#rest-api-endpoints)


Additionally, the simulator offers custom endpoints:

- `simulator/generate-blocks/:num`: This endpoint initiates the generation of a specified number of blocks for each shard.