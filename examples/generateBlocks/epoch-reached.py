import sys

from multiversx_sdk import ProxyNetworkProvider

SIMULATOR_URL = "http://localhost:8085"
GENERATE_BLOCKS_UNTIL_EPOCH_REACHED_URL = "simulator/generate-blocks-until-epoch-reached"
NETWORK_STATUS_URL = "network/status/4294967295"


def main():
    # create a network provider
    provider = ProxyNetworkProvider(SIMULATOR_URL)

    target_epoch = 10
    # generate blocks until we reach the target epoch
    provider.do_post_generic(f"{GENERATE_BLOCKS_UNTIL_EPOCH_REACHED_URL}/{target_epoch}", {})

    network_status = provider.get_network_status()  # will default to metachain

    epoch_number = network_status.raw.get("erd_epoch_number", 0)
    if epoch_number < target_epoch:
        sys.exit(f"epoch {target_epoch} not reached")

    print(f"successfully created blocks and epoch {target_epoch} was reached")


if __name__ == "__main__":
    main()
