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

# run adder example
run_python_script ../../examples/contracts/adder/ adder.py

# run wrapped egld example
run_python_script ../../examples/contracts/wrappedegld wrapped-egld.py

# run esdt create example
run_python_script ../../examples/esdt/ issue-fungible.py

# run staking example
run_python_script ../../examples/staking staking.py