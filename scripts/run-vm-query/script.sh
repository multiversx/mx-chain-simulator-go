SIMULATOR_URL=http://localhost:8085

wait_simulator_to_start() {
    endpoint="${SIMULATOR_URL}/network/config"
    for ((i = 1; i <= 10; i++)); do
        if curl -s -o /dev/null "$endpoint" >/dev/null 2>&1; then
            return 0
        fi
        sleep "0.1"
    done

    echo "Error: Timed out waiting for endpoint '$endpoint' to become reachable."
    return 1
}

wait_simulator_to_start

ADDRESS=$(curl -s ''${SIMULATOR_URL}'/simulator/initial-wallets' | jq -r '.data.stakeWallets[0].address.bech32')


RET_CODE=$(curl --location ''${SIMULATOR_URL}'/vm-values/query' \
--header 'Content-Type: application/json' \
--data '{
  "scAddress": "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l",
  "funcName": "getTotalStaked",
  "caller":"'"$ADDRESS"'"
}' | jq -r '.data.data.returnCode')

if [ "$RET_CODE" = "ok" ]; then
    echo "The return code is ok."
else
    echo "The return code is not ok. It is $RET_CODE."
    exit 1
fi

