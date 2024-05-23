package facade

import (
	"encoding/hex"
	"testing"

	"github.com/multiversx/mx-chain-go/node/chainSimulator/dtos"
	dtoc "github.com/multiversx/mx-chain-simulator-go/pkg/dtos"
	"github.com/multiversx/mx-chain-simulator-go/testscommon"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNewSimulatorFacade(t *testing.T) {
	t.Parallel()

	t.Run("nil simulator should error", func(t *testing.T) {
		t.Parallel()

		facade, err := NewSimulatorFacade(nil)
		require.Equal(t, errNilSimulatorHandler, err)
		require.Nil(t, facade)
	})
	t.Run("should work", func(t *testing.T) {
		t.Parallel()

		facade, err := NewSimulatorFacade(&testscommon.SimulatorHandlerMock{})
		require.NoError(t, err)
		require.NotNil(t, facade)
	})
}

func TestSimulatorFacade_IsInterfaceNil(t *testing.T) {
	t.Parallel()

	var facade *simulatorFacade
	require.True(t, facade.IsInterfaceNil())

	facade, _ = NewSimulatorFacade(&testscommon.SimulatorHandlerMock{})
	require.False(t, facade.IsInterfaceNil())
}

func TestSimulatorFacade_GenerateBlocks(t *testing.T) {
	t.Parallel()

	cnt := 0
	facade, err := NewSimulatorFacade(&testscommon.SimulatorHandlerMock{
		GenerateBlocksCalled: func(numOfBlocks int) error {
			cnt++
			return nil
		},
	})
	require.NoError(t, err)

	err = facade.GenerateBlocks(0)
	require.Equal(t, errInvalidNumOfBlocks, err)

	err = facade.GenerateBlocks(1)
	require.NoError(t, err)
	require.Equal(t, 1, cnt)
}

func TestSimulatorFacade_GetInitialWalletKeys(t *testing.T) {
	t.Parallel()

	wasCalled := false
	providedInitialWalletKeys := &dtos.InitialWalletKeys{}
	facade, err := NewSimulatorFacade(&testscommon.SimulatorHandlerMock{
		GetInitialWalletKeysCalled: func() *dtos.InitialWalletKeys {
			wasCalled = true
			return providedInitialWalletKeys
		},
	})
	require.NoError(t, err)

	walletKeys := facade.GetInitialWalletKeys()
	require.True(t, walletKeys == providedInitialWalletKeys) // pointer testing
	require.True(t, wasCalled)
}

func TestSimulatorFacade_SetKeyValueForAddress(t *testing.T) {
	t.Parallel()

	wasCalled := false
	providedAddress := "address"
	providedKeyValue := map[string]string{"key1": "value1"}
	facade, err := NewSimulatorFacade(&testscommon.SimulatorHandlerMock{
		SetKeyValueForAddressCalled: func(address string, keyValueMap map[string]string) error {
			wasCalled = true
			require.Equal(t, providedAddress, address)
			require.Equal(t, providedKeyValue, keyValueMap)

			return nil
		},
	})
	require.NoError(t, err)

	err = facade.SetKeyValueForAddress(providedAddress, providedKeyValue)
	require.NoError(t, err)
	require.True(t, wasCalled)
}

func TestSimulatorFacade_SetStateMultiple(t *testing.T) {
	t.Parallel()

	wasCalled := false
	providedStateSlice := []*dtos.AddressState{{}}
	facade, err := NewSimulatorFacade(&testscommon.SimulatorHandlerMock{
		SetStateMultipleCalled: func(stateSlice []*dtos.AddressState) error {
			wasCalled = true
			require.Equal(t, providedStateSlice, stateSlice)

			return nil
		},
	})
	require.NoError(t, err)

	err = facade.SetStateMultiple(providedStateSlice, true)
	require.NoError(t, err)
	require.True(t, wasCalled)
}

func TestSimulatorFacade_GenerateBlocksUntilEpochIsReached(t *testing.T) {
	t.Parallel()

	testEpoch := int32(37)
	generateBlocksCalled := false
	simulator := &testscommon.SimulatorHandlerMock{
		GenerateBlocksUntilEpochIsReachedCalled: func(targetEpoch int32) error {
			assert.Equal(t, testEpoch, targetEpoch)
			generateBlocksCalled = true
			return nil
		},
	}

	facade, _ := NewSimulatorFacade(simulator)
	err := facade.GenerateBlocksUntilEpochIsReached(testEpoch)
	assert.Nil(t, err)
	assert.True(t, generateBlocksCalled)
}

func TestSimulatorFacade_AddValidatorKeys(t *testing.T) {
	t.Parallel()

	t.Run("invalid base64 key should error", func(t *testing.T) {
		t.Parallel()

		providedValidators := &dtoc.ValidatorKeys{
			PrivateKeysBase64: []string{
				"invalid",
			},
		}
		facade, err := NewSimulatorFacade(&testscommon.SimulatorHandlerMock{
			AddValidatorKeysCalled: func(validatorsPrivateKeys [][]byte) error {
				require.Fail(t, "should have not been called")

				return nil
			},
		})
		require.NoError(t, err)

		err = facade.AddValidatorKeys(providedValidators)
		require.Error(t, err)
	})
	t.Run("invalid hex decoding should error", func(t *testing.T) {
		t.Parallel()

		providedValidators := &dtoc.ValidatorKeys{
			PrivateKeysBase64: []string{
				"dGhpcyBpcyBub3QgYSBoZXggc3RyaW5n", // "this is not a hex string"
			},
		}
		facade, err := NewSimulatorFacade(&testscommon.SimulatorHandlerMock{
			AddValidatorKeysCalled: func(validatorsPrivateKeys [][]byte) error {
				require.Fail(t, "should have not been called")

				return nil
			},
		})
		require.NoError(t, err)

		err = facade.AddValidatorKeys(providedValidators)
		require.Error(t, err)
	})
	t.Run("should work", func(t *testing.T) {
		t.Parallel()

		wasCalled := false
		providedValidators := &dtoc.ValidatorKeys{
			PrivateKeysBase64: []string{
				"NGRmMmM1ZDYzNzEwMWI1MDc3NDFhZWMyODIwOWYxYTQ0NDM2NGU3N2RlNjFkZGIy\nOTY3YzA1OGRkZGFiODYxZg==",
				"MWE1ZjIxYWFkMTRlOTA0ZDc4YjdiNGE1OTU0NWVmMmRjMjM2N2Q3MDMwNzNkYzdm\nN2U2OTljMDBhODMzMDY2MA==",
			},
		}
		key1, _ := hex.DecodeString("4df2c5d637101b507741aec28209f1a444364e77de61ddb2967c058dddab861f")
		key2, _ := hex.DecodeString("1a5f21aad14e904d78b7b4a59545ef2dc2367d703073dc7f7e699c00a8330660")
		expectedValidatorsPrivateKeys := [][]byte{
			key1,
			key2,
		}
		facade, err := NewSimulatorFacade(&testscommon.SimulatorHandlerMock{
			AddValidatorKeysCalled: func(validatorsPrivateKeys [][]byte) error {
				wasCalled = true
				require.Equal(t, expectedValidatorsPrivateKeys, validatorsPrivateKeys)

				return nil
			},
		})
		require.NoError(t, err)

		err = facade.AddValidatorKeys(providedValidators)
		require.NoError(t, err)
		require.True(t, wasCalled)
	})
}

func TestSimulatorFacade_ForceUpdateValidatorStatistics(t *testing.T) {
	t.Parallel()

	forceResetCalled := false
	simulator := &testscommon.SimulatorHandlerMock{
		ForceResetValidatorStatisticsCacheCalled: func() error {
			forceResetCalled = true
			return nil
		},
	}

	facade, _ := NewSimulatorFacade(simulator)
	err := facade.ForceUpdateValidatorStatistics()
	assert.Nil(t, err)
	assert.True(t, forceResetCalled)
}

func TestSimulatorFacade_GetObserversInfo(t *testing.T) {
	t.Parallel()

	simulator := &testscommon.SimulatorHandlerMock{
		GetRestAPIInterfacesCalled: func() map[uint32]string {
			return map[uint32]string{
				0: ":1234",
				1: "localhost:2233",
			}
		},
	}

	facade, _ := NewSimulatorFacade(simulator)
	response, err := facade.GetObserversInfo()
	require.NoError(t, err)
	require.Equal(t, map[uint32]*dtoc.ObserverInfo{
		0: {APIPort: 1234},
		1: {APIPort: 2233},
	}, response)
}
