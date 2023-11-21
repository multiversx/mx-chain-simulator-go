package api

import "github.com/multiversx/mx-chain-go/node/chainSimulator/dtos"

// SimulatorFacade defines what a simulator facade should be able to do
type SimulatorFacade interface {
	GenerateBlocks(numOfBlocks int) error
	GetInitialWalletKeys() *dtos.InitialWalletKeys
	SetState(address string, keyValueMap map[string]string) error
	IsInterfaceNil() bool
}
