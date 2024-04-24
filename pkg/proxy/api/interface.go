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
	SetStateMultipleOverwrite(stateSlice []*dtos.AddressState) error
	AddValidatorKeys(validators *dtosc.ValidatorKeys) error
	GenerateBlocksUntilEpochIsReached(targetEpoch int32) error
	ForceUpdateValidatorStatistics() error
	IsInterfaceNil() bool
}
