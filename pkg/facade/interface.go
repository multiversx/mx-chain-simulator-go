package facade

import "github.com/multiversx/mx-chain-go/node/chainSimulator/dtos"

// SimulatorHandler defines what a simulator handler should be able to do
type SimulatorHandler interface {
	GetInitialWalletKeys() *dtos.InitialWalletKeys
	GenerateBlocks(numOfBlocks int) error
	SetKeyValueForAddress(address string, keyValueMap map[string]string) error
	SetStateMultiple(stateSlice []*dtos.AddressState) error
	RemoveAccounts(addresses []string) error
	AddValidatorKeys(validatorsPrivateKeys [][]byte) error
	GenerateBlocksUntilEpochIsReached(targetEpoch int32) error
	ForceResetValidatorStatisticsCache() error
	GetRestAPIInterfaces() map[uint32]string
	IsInterfaceNil() bool
}
