SOVEREIGN_BRANCH="feat/chain-go-sdk"

cd ..
git clone https://github.com/multiversx/mx-chain-go.git
cd mx-chain-go
git fetch
git checkout $SOVEREIGN_BRANCH
