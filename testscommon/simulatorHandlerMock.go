package testscommon

import "github.com/multiversx/mx-chain-go/node/chainSimulator/dtos"

// SimulatorHandlerMock -
type SimulatorHandlerMock struct {
	GetInitialWalletKeysCalled               func() *dtos.InitialWalletKeys
	GenerateBlocksCalled                     func(numOfBlocks int) error
	SetKeyValueForAddressCalled              func(address string, keyValueMap map[string]string) error
	SetStateMultipleCalled                   func(stateSlice []*dtos.AddressState) error
	AddValidatorKeysCalled                   func(validatorsPrivateKeys [][]byte) error
	GenerateBlocksUntilEpochIsReachedCalled  func(targetEpoch int32) error
	ForceResetValidatorStatisticsCacheCalled func() error
	RemoveAccountsCalled                     func(addresses []string) error
	GetRestAPIInterfacesCalled               func() map[uint32]string
	ForceChangeOfEpochCalled                 func() error
}

// ForceChangeOfEpoch -
func (mock *SimulatorHandlerMock) ForceChangeOfEpoch() error {
	if mock.ForceChangeOfEpochCalled != nil {
		return mock.ForceChangeOfEpochCalled()
	}

	return nil
}

// GetRestAPIInterfaces -
func (mock *SimulatorHandlerMock) GetRestAPIInterfaces() map[uint32]string {
	if mock.GetRestAPIInterfacesCalled != nil {
		return mock.GetRestAPIInterfacesCalled()
	}

	return nil
}

// RemoveAccounts -
func (mock *SimulatorHandlerMock) RemoveAccounts(addresses []string) error {
	if mock.RemoveAccountsCalled != nil {
		return mock.RemoveAccountsCalled(addresses)
	}

	return nil
}

// GetInitialWalletKeys -
func (mock *SimulatorHandlerMock) GetInitialWalletKeys() *dtos.InitialWalletKeys {
	if mock.GetInitialWalletKeysCalled != nil {
		return mock.GetInitialWalletKeysCalled()
	}
	return nil
}

// GenerateBlocks -
func (mock *SimulatorHandlerMock) GenerateBlocks(numOfBlocks int) error {
	if mock.GenerateBlocksCalled != nil {
		return mock.GenerateBlocksCalled(numOfBlocks)
	}
	return nil
}

// SetKeyValueForAddress -
func (mock *SimulatorHandlerMock) SetKeyValueForAddress(address string, keyValueMap map[string]string) error {
	if mock.SetKeyValueForAddressCalled != nil {
		return mock.SetKeyValueForAddressCalled(address, keyValueMap)
	}
	return nil
}

// SetStateMultiple -
func (mock *SimulatorHandlerMock) SetStateMultiple(stateSlice []*dtos.AddressState) error {
	if mock.SetStateMultipleCalled != nil {
		return mock.SetStateMultipleCalled(stateSlice)
	}
	return nil
}

// AddValidatorKeys -
func (mock *SimulatorHandlerMock) AddValidatorKeys(validatorsPrivateKeys [][]byte) error {
	if mock.AddValidatorKeysCalled != nil {
		return mock.AddValidatorKeysCalled(validatorsPrivateKeys)
	}
	return nil
}

// GenerateBlocksUntilEpochIsReached -
func (mock *SimulatorHandlerMock) GenerateBlocksUntilEpochIsReached(targetEpoch int32) error {
	if mock.GenerateBlocksUntilEpochIsReachedCalled != nil {
		return mock.GenerateBlocksUntilEpochIsReachedCalled(targetEpoch)
	}

	return nil
}

// ForceResetValidatorStatisticsCache -
func (mock *SimulatorHandlerMock) ForceResetValidatorStatisticsCache() error {
	if mock.ForceResetValidatorStatisticsCacheCalled != nil {
		return mock.ForceResetValidatorStatisticsCacheCalled()
	}

	return nil
}

// IsInterfaceNil -
func (mock *SimulatorHandlerMock) IsInterfaceNil() bool {
	return mock == nil
}
