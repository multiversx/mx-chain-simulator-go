SIMULATOR_URL="http://localhost:8085"
MY_ADDR="erd1r87hlp37eqdf25ydxd4pasc3tqp8suztzm7x4xnv53f5phzuyk3s2g7yn4"


# Call faucet for my address
curl --request POST \
  --url ${SIMULATOR_URL}/transaction/send-user-funds \
  --header 'Content-Type: application/json' \
  --data '{
	"receiver":"'${MY_ADDR}'"
}'

sleep 0.2

# Generate 1 block
curl --request POST \
  --url ${SIMULATOR_URL}/simulator/generate-blocks/1

api_response=$(curl --request GET --url ${SIMULATOR_URL}/address/${MY_ADDR})

# Use jq to parse the JSON and extract the balance field
balance=$(echo "$api_response" | jq -r '.data.account.balance')

# Compare the balance with the expected balance
EXPECTED_BALANCE="10000000000000000000"
if [ "$balance" != "$EXPECTED_BALANCE" ]; then
  echo "Error: Balance $balance does not match expected balance $EXPECTED_BALANCE"
  exit 1
else
  echo "Balance: $balance"
fi
