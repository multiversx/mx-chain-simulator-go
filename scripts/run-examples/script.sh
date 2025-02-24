#!/bin/bash

CHAIN_SIMULATOR_URL=http://localhost:8085

# this will stop the script execution if a command returns an error
set -e

run_python_script() {
    pushd "$1" || return
    python3 "$2"
    popd || return
}

wait_simulator_to_start() {
    local endpoint="${CHAIN_SIMULATOR_URL}/network/config"
    local max_attempts="10"
    local wait_interval_in_seconds="6"

    echo $endpoint

    for ((i = 1; i <= max_attempts; i++)); do
        if [ $(curl -s -o /dev/null -w "%{http_code}" "$endpoint") -eq 200 ]; then
            echo "Endpoint '$endpoint' is reachable."
            return 0
        fi
        sleep "$wait_interval_in_seconds"
    done

    echo "Error: Timed out waiting for endpoint '$endpoint' to become reachable."
    return 1
}

wait_simulator_to_start

# TODO MX-16498 investigate staking test
# run staking example
# run_python_script ../../examples/staking staking.py

# run adder example
run_python_script ../../examples/contracts/adder/ adder.py

# run wrapped egld example
# run_python_script ../../examples/contracts/wrappedegld wrapped-egld.py

# run esdt create example
run_python_script ../../examples/esdt/ issue-fungible.py

# run move balance example
run_python_script ../../examples/movebalance move-balance.py

# run generate blocks until epoch is reached example
run_python_script ../../examples/generateBlocks epoch-reached.py

# run set state examples
run_python_script ../../examples/setState code-metadata.py

# TODO MX-16493 SC issue bug
# run deploy with issue esdt
# run_python_script ../../examples/contracts/issue-esdt-with-contract issue-with-contract.py

# run deploy SC with custom crypto primitives in VM
run_python_script ../../examples/contracts/basic-features-crypto basic-features-crypto.py
