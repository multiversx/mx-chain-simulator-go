package facade

import "github.com/multiversx/mx-chain-go/node/chainSimulator/dtos"

// SimulatorHandler defines what a simulator handler should be able to do
type SimulatorHandler interface {
	GetInitialWalletKeys() *dtos.InitialWalletKeys
	GenerateBlocks(numOfBlocks int) error
	SetState(address string, keyValueMap map[string]string) error
	IsInterfaceNil() bool
}
