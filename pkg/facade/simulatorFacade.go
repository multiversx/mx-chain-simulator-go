package facade

import (
	"errors"

	"github.com/multiversx/mx-chain-core-go/core/check"
)

type simulatorFacade struct {
	simulator SimulatorHandler
}

func NewSimulatorFacade(simulator SimulatorHandler) (*simulatorFacade, error) {
	if check.IfNil(simulator) {
		return nil, errors.New("nil simulator handler ")
	}

	return &simulatorFacade{
		simulator: simulator,
	}, nil
}

func (sf *simulatorFacade) GenerateBlocks(numOfBlocks int) error {
	if numOfBlocks <= 0 {
		return errors.New("num of blocks must be greater than zero")
	}
	return sf.simulator.GenerateBlocks(numOfBlocks)
}

func (sf *simulatorFacade) IsInterfaceNil() bool {
	return sf == nil
}
