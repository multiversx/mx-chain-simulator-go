package api

import (
	"github.com/multiversx/mx-chain-go/node/chainSimulator/dtos"
	dtosc "github.com/multiversx/mx-chain-simulator-go/pkg/dtos"
)

// SimulatorFacade defines what a simulator facade should be able to do
type SimulatorFacade interface {
	GenerateBlocks(numOfBlocks int) error
	GetInitialWalletKeys() *dtos.InitialWalletKeys
	SetKeyValueForAddress(address string, keyValueMap map[string]string) error
	SetStateMultiple(stateSlice []*dtos.AddressState) error
	AddValidatorsKeys(validators *dtosc.ValidatorsKeys) error
	IsInterfaceNil() bool
}
