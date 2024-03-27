package process

import (
	"errors"
	"sync/atomic"
	"testing"
	"time"

	"github.com/multiversx/mx-chain-simulator-go/testscommon"
	"github.com/stretchr/testify/require"
)

func TestNewBlocksGenerator(t *testing.T) {
	t.Parallel()

	t.Run("nil simulator should error", func(t *testing.T) {
		t.Parallel()

		args := ArgBlocksGenerator{
			Simulator:     nil,
			BlockTimeInMs: 0,
		}
		generator, err := NewBlocksGenerator(args)
		require.Equal(t, errNilChainSimulator, err)
		require.Nil(t, generator)
	})
	t.Run("invalid block time should error", func(t *testing.T) {
		t.Parallel()

		args := ArgBlocksGenerator{
			Simulator:     &testscommon.SimulatorHandlerMock{},
			BlockTimeInMs: 0,
		}
		generator, err := NewBlocksGenerator(args)
		require.True(t, errors.Is(err, errInvalidValue))
		require.Nil(t, generator)
	})
	t.Run("should work", func(t *testing.T) {
		t.Parallel()

		providedBlockTime := uint64(100)
		chanDone := make(chan struct{})
		cnt := uint32(0)
		args := ArgBlocksGenerator{
			Simulator: &testscommon.SimulatorHandlerMock{
				GenerateBlocksCalled: func(numOfBlocks int) error {
					require.Equal(t, 1, numOfBlocks)

					atomic.AddUint32(&cnt, 1)
					if atomic.LoadUint32(&cnt) == 1 {
						return errors.New("expected error") // for coverage only
					}

					chanDone <- struct{}{}

					return nil
				},
			},
			BlockTimeInMs: providedBlockTime,
		}
		generator, err := NewBlocksGenerator(args)
		require.NoError(t, err)
		require.NotNil(t, generator)

		for {
			select {
			case <-chanDone:
				generator.Close()
				return
			case <-time.After(time.Duration(providedBlockTime*3) * time.Millisecond):
				generator.Close()
				require.Fail(t, "timeout")
				return
			}
		}
	})
}
