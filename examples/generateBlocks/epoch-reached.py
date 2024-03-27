import sys

from multiversx_sdk_network_providers import ProxyNetworkProvider

SIMULATOR_URL = "http://localhost:8085"
GENERATE_BLOCKS_UNTIL_EPOCH_REACHED_URL = f"{SIMULATOR_URL}/simulator/generate-blocks-until-epoch-reached"
NETWORK_STATUS_URL = f"{SIMULATOR_URL}/network/status/4294967295"


def main():
    # create a network provider
    provider = ProxyNetworkProvider(SIMULATOR_URL)

    targetEpoch = 10
    # generate blocks until we reach the target epoch
    provider.do_post(f"{GENERATE_BLOCKS_UNTIL_EPOCH_REACHED_URL}/{targetEpoch}", {})

    network_status = provider.get_network_status()  # will default to metachain

    if network_status.epoch_number < targetEpoch:
       sys.exit(f"epoch {targetEpoch} not reached")

    print(f"successfully created blocks and epoch {targetEpoch} was reached")


if __name__ == "__main__":
    main()
