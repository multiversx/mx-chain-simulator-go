import sys

from multiversx_sdk_network_providers import ProxyNetworkProvider

SIMULATOR_URL = "http://localhost:8085"
GENERATE_BLOCKS_UNTIL_EPOCH_REACHED_URL = f"{SIMULATOR_URL}/simulator/generate-blocks-until-epoch-reached"
NETWORK_STATUS_URL = f"{SIMULATOR_URL}/network/status/4294967295"


def main():
    # create a network provider
    provider = ProxyNetworkProvider(SIMULATOR_URL)

    # generate blocks until we reach the epoch 10
    provider.do_post(f"{GENERATE_BLOCKS_UNTIL_EPOCH_REACHED_URL}/10", {})

    network_status = provider.get_network_status()  # will default to metachain

    if network_status.epoch_number < 10:
       sys.exit(f"epoch 10 not reached")

    print("successfully created blocks and epoch 10 was reached")


if __name__ == "__main__":
    main()
