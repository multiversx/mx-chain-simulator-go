package facade

import "github.com/multiversx/mx-chain-go/node/chainSimulator/dtos"

type SimulatorHandler interface {
	GetInitialWalletKeys() *dtos.InitialWalletKeys
	GenerateBlocks(numOfBlocks int) error
	IsInterfaceNil() bool
}
