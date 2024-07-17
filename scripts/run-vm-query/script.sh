SIMULATOR_URL=http://localhost:8085
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

