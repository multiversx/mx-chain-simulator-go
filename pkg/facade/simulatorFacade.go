package facade

import (
	"errors"

	"github.com/multiversx/mx-chain-core-go/core/check"
	"github.com/multiversx/mx-chain-go/node/chainSimulator/dtos"
)

type simulatorFacade struct {
	simulator SimulatorHandler
}

// NewSimulatorFacade will create a new instance of simulatorFacade
func NewSimulatorFacade(simulator SimulatorHandler) (*simulatorFacade, error) {
	if check.IfNil(simulator) {
		return nil, errors.New("nil simulator handler ")
	}

	return &simulatorFacade{
		simulator: simulator,
	}, nil
}

// GenerateBlocks will generate a provided number of blocks
func (sf *simulatorFacade) GenerateBlocks(numOfBlocks int) error {
	if numOfBlocks <= 0 {
		return errors.New("num of blocks must be greater than zero")
	}
	return sf.simulator.GenerateBlocks(numOfBlocks)
}

// GetInitialWalletKeys will return the initial wallets
func (sf *simulatorFacade) GetInitialWalletKeys() *dtos.InitialWalletKeys {
	return sf.simulator.GetInitialWalletKeys()
}

// IsInterfaceNil returns true if there is no value under the interface
func (sf *simulatorFacade) IsInterfaceNil() bool {
	return sf == nil
}
