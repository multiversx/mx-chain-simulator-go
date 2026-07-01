package facade

import (
	"encoding/hex"
	"errors"
	"strings"
	"sync"
	"testing"

	"github.com/multiversx/mx-chain-core-go/core"
	coreData "github.com/multiversx/mx-chain-core-go/data"
	"github.com/multiversx/mx-chain-core-go/data/block"
	"github.com/multiversx/mx-chain-core-go/data/transaction"
	"github.com/multiversx/mx-chain-core-go/marshal"
	"github.com/multiversx/mx-chain-go/dataRetriever"
	"github.com/multiversx/mx-chain-go/factory"
	"github.com/multiversx/mx-chain-go/factory/mock"
	"github.com/multiversx/mx-chain-go/node/chainSimulator/dtos"
	"github.com/multiversx/mx-chain-go/node/chainSimulator/process"
	"github.com/multiversx/mx-chain-go/sharding"
	"github.com/multiversx/mx-chain-go/storage"
	chainTestsCommon "github.com/multiversx/mx-chain-go/testscommon"
	storageStubs "github.com/multiversx/mx-chain-go/testscommon/storage"
	"github.com/multiversx/mx-chain-proxy-go/data"
	dtoc "github.com/multiversx/mx-chain-simulator-go/pkg/dtos"
	"github.com/multiversx/mx-chain-simulator-go/testscommon"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestNewSimulatorFacade(t *testing.T) {
	t.Parallel()

	t.Run("nil simulator should error", func(t *testing.T) {
		t.Parallel()

		facade, err := NewSimulatorFacade(nil, &testscommon.TransactionHandlerMock{})
		require.Equal(t, errNilSimulatorHandler, err)
		require.Nil(t, facade)
	})
	t.Run("should work", func(t *testing.T) {
		t.Parallel()

		facade, err := NewSimulatorFacade(&testscommon.SimulatorHandlerMock{}, &testscommon.TransactionHandlerMock{})
		require.NoError(t, err)
		require.NotNil(t, facade)
	})
}

func TestSimulatorFacade_IsInterfaceNil(t *testing.T) {
	t.Parallel()

	var facade *simulatorFacade
	require.True(t, facade.IsInterfaceNil())

	facade, _ = NewSimulatorFacade(&testscommon.SimulatorHandlerMock{}, &testscommon.TransactionHandlerMock{})
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
	}, &testscommon.TransactionHandlerMock{})
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
	}, &testscommon.TransactionHandlerMock{})
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
	}, &testscommon.TransactionHandlerMock{})
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
	}, &testscommon.TransactionHandlerMock{})
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

	facade, _ := NewSimulatorFacade(simulator, &testscommon.TransactionHandlerMock{})
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
		}, &testscommon.TransactionHandlerMock{})
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
		}, &testscommon.TransactionHandlerMock{})
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
		}, &testscommon.TransactionHandlerMock{})
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

	facade, _ := NewSimulatorFacade(simulator, &testscommon.TransactionHandlerMock{})
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

	facade, _ := NewSimulatorFacade(simulator, &testscommon.TransactionHandlerMock{})
	response, err := facade.GetObserversInfo()
	require.NoError(t, err)
	require.Equal(t, map[uint32]*dtoc.ObserverInfo{
		0: {APIPort: 1234},
		1: {APIPort: 2233},
	}, response)
}

func TestSimulatorFacade_GenerateBlocksUntilTransactionIsProcessed_CannotGetTxStatusInfo(t *testing.T) {
	t.Parallel()

	expectedErr := errors.New("expected error")

	simulator := &testscommon.SimulatorHandlerMock{}

	facade, _ := NewSimulatorFacade(simulator, &testscommon.TransactionHandlerMock{
		GetProcessedTransactionStatusCalled: func(txHash string) (*data.ProcessStatusResponse, error) {
			return nil, expectedErr
		},
	})

	err := facade.GenerateBlocksUntilTransactionIsProcessed("txHash", 20)
	require.Equal(t, expectedErr, err)
}

func TestSimulatorFacade_GenerateBlocksUntilTransactionIsProcessed_CannotGenerateBlockErr(t *testing.T) {
	t.Parallel()

	expectedErr := errors.New("cannot generate block")

	simulator := &testscommon.SimulatorHandlerMock{
		GenerateBlocksCalled: func(numOfBlocks int) error {
			return expectedErr
		},
	}

	facade, _ := NewSimulatorFacade(simulator, &testscommon.TransactionHandlerMock{

		GetProcessedTransactionStatusCalled: func(txHash string) (*data.ProcessStatusResponse, error) {
			return &data.ProcessStatusResponse{
				Status: transaction.TxStatusPending.String(),
			}, nil
		},
	})

	err := facade.GenerateBlocksUntilTransactionIsProcessed("txHash", 20)
	require.Equal(t, expectedErr, err)
}

func TestSimulatorFacade_GenerateBlocksUntilTransactionIsProcessed_ErrPendingTransaction(t *testing.T) {
	t.Parallel()

	simulator := &testscommon.SimulatorHandlerMock{
		GenerateBlocksCalled: func(numOfBlocks int) error {
			return nil
		},
	}

	facade, _ := NewSimulatorFacade(simulator, &testscommon.TransactionHandlerMock{
		GetProcessedTransactionStatusCalled: func(txHash string) (*data.ProcessStatusResponse, error) {
			return &data.ProcessStatusResponse{
				Status: transaction.TxStatusPending.String(),
			}, nil
		},
	})

	err := facade.GenerateBlocksUntilTransactionIsProcessed("txHash", 20)
	require.Equal(t, errPendingTransaction, err)
}

func TestSimulatorFacade_GenerateBlocksUntilTransactionIsProcessed_ShouldWork(t *testing.T) {
	t.Parallel()

	count := 0
	simulator := &testscommon.SimulatorHandlerMock{
		GenerateBlocksCalled: func(numOfBlocks int) error {
			return nil
		},
	}

	facade, _ := NewSimulatorFacade(simulator, &testscommon.TransactionHandlerMock{
		GetProcessedTransactionStatusCalled: func(txHash string) (*data.ProcessStatusResponse, error) {
			count++
			if count == 1 {
				return &data.ProcessStatusResponse{
					Status: transaction.TxStatusFail.String(),
				}, nil
			}
			return &data.ProcessStatusResponse{
				Status: transaction.TxStatusPending.String(),
			}, nil
		},
	})

	err := facade.GenerateBlocksUntilTransactionIsProcessed("txHash", 20)
	require.Nil(t, err)
}

func TestSimulatorFacade_ForceChangeOfEpoch_TargetEpochLowerThanCurrentEpoch(t *testing.T) {
	t.Parallel()

	epoch := uint32(10)
	simulator := &testscommon.SimulatorHandlerMock{
		GetNodeHandlerCalled: func(shardID uint32) process.NodeHandler {
			return getNodeHandlerWithCurrentEpoch(epoch)
		},
	}

	facade, _ := NewSimulatorFacade(simulator, &testscommon.TransactionHandlerMock{})

	err := facade.ForceChangeOfEpoch(5)
	require.NotNil(t, err)
	require.True(t, strings.Contains(err.Error(), errMsgTargetEpochLowerThanCurrentEpoch))
}

func TestSimulatorFacade_ForceChangeOfEpochError(t *testing.T) {
	epoch := uint32(0)
	expectedErr := errors.New("expected error")
	simulator := &testscommon.SimulatorHandlerMock{
		GetNodeHandlerCalled: func(shardID uint32) process.NodeHandler {
			epoch++
			return getNodeHandlerWithCurrentEpoch(epoch)
		},
		ForceChangeOfEpochCalled: func() error {
			return expectedErr
		},
	}

	facade, _ := NewSimulatorFacade(simulator, &testscommon.TransactionHandlerMock{})

	err := facade.ForceChangeOfEpoch(5)
	require.Equal(t, expectedErr, err)
}

func TestSimulatorFacade_ForceChangeOfEpoch(t *testing.T) {
	epoch := uint32(0)
	simulator := &testscommon.SimulatorHandlerMock{
		GetNodeHandlerCalled: func(shardID uint32) process.NodeHandler {
			epoch++
			return getNodeHandlerWithCurrentEpoch(epoch)
		},
	}

	facade, _ := NewSimulatorFacade(simulator, &testscommon.TransactionHandlerMock{})

	err := facade.ForceChangeOfEpoch(5)
	require.Nil(t, err)
}

func TestSimulatorFacade_SetEpochStartHeader(t *testing.T) {
	t.Parallel()

	marshaller := &marshal.GogoProtoMarshalizer{}

	newSimulator := func(genesisHeader coreData.HeaderHandler, numShards uint32, putHandler func(shardID uint32, unitType dataRetriever.UnitType, key, value []byte) error) *testscommon.SimulatorHandlerMock {
		return &testscommon.SimulatorHandlerMock{
			GetNodeHandlerCalled: func(shardID uint32) process.NodeHandler {
				return &testscommon.NodeHandlerStub{
					GetShardCoordinatorCalled: func() sharding.Coordinator {
						return &chainTestsCommon.ShardsCoordinatorMock{NoShards: numShards}
					},
					GetCoreComponentsCalled: func() factory.CoreComponentsHolder {
						return &mock.CoreComponentsMock{IntMarsh: marshaller}
					},
					GetDataComponentsCalled: func() factory.DataComponentsHolder {
						return &mock.DataComponentsMock{
							Blkc: &chainTestsCommon.ChainHandlerStub{
								GetGenesisHeaderCalled: func() coreData.HeaderHandler {
									return genesisHeader
								},
							},
							Storage: &storageStubs.ChainStorerStub{
								GetStorerCalled: func(unitType dataRetriever.UnitType) (storage.Storer, error) {
									return &storageStubs.StorerStub{
										PutCalled: func(key, value []byte) error {
											return putHandler(shardID, unitType, key, value)
										},
									}, nil
								},
							},
						}
					},
				}
			},
		}
	}

	t.Run("non-zero initial epoch should persist the genesis header for each shard and metachain", func(t *testing.T) {
		t.Parallel()

		epoch := uint32(7)
		numShards := uint32(2)
		genesisHeader := &block.MetaBlock{Epoch: epoch}
		expectedValue, errMarshal := marshaller.Marshal(genesisHeader)
		require.Nil(t, errMarshal)
		expectedKey := []byte(core.EpochStartIdentifier(epoch))

		var mutStored sync.Mutex
		storedUnits := make(map[uint32]dataRetriever.UnitType)

		simulator := newSimulator(genesisHeader, numShards, func(shardID uint32, unitType dataRetriever.UnitType, key, value []byte) error {
			mutStored.Lock()
			defer mutStored.Unlock()

			assert.Equal(t, expectedKey, key)
			assert.Equal(t, expectedValue, value)
			storedUnits[shardID] = unitType
			return nil
		})

		facade, _ := NewSimulatorFacade(simulator, &testscommon.TransactionHandlerMock{})

		err := facade.SetEpochStartHeader()
		require.Nil(t, err)

		// shard 0, shard 1 and metachain
		require.Len(t, storedUnits, int(numShards)+1)
		assert.Equal(t, dataRetriever.BlockHeaderUnit, storedUnits[0])
		assert.Equal(t, dataRetriever.BlockHeaderUnit, storedUnits[1])
		assert.Equal(t, dataRetriever.MetaBlockUnit, storedUnits[core.MetachainShardId])
	})

	t.Run("initial epoch 0 should be a no-op", func(t *testing.T) {
		t.Parallel()

		genesisHeader := &block.MetaBlock{Epoch: 0}
		putCalled := false
		simulator := newSimulator(genesisHeader, 1, func(_ uint32, _ dataRetriever.UnitType, _, _ []byte) error {
			putCalled = true
			return nil
		})

		facade, _ := NewSimulatorFacade(simulator, &testscommon.TransactionHandlerMock{})

		err := facade.SetEpochStartHeader()
		require.Nil(t, err)
		assert.False(t, putCalled)
	})

	t.Run("put error should be propagated", func(t *testing.T) {
		t.Parallel()

		expectedErr := errors.New("put error")
		genesisHeader := &block.MetaBlock{Epoch: 3}
		simulator := newSimulator(genesisHeader, 1, func(_ uint32, _ dataRetriever.UnitType, _, _ []byte) error {
			return expectedErr
		})

		facade, _ := NewSimulatorFacade(simulator, &testscommon.TransactionHandlerMock{})

		err := facade.SetEpochStartHeader()
		require.Equal(t, expectedErr, err)
	})
}

func getNodeHandlerWithCurrentEpoch(epoch uint32) process.NodeHandler {
	return &testscommon.NodeHandlerStub{
		GetProcessComponentsCalled: func() factory.ProcessComponentsHolder {
			return &mock.ProcessComponentsMock{
				EpochTrigger: &mock.EpochStartTriggerStub{
					EpochCalled: func() uint32 {
						return epoch
					},
				},
			}
		},
	}
}
