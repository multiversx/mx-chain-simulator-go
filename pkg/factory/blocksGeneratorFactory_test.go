package factory

import (
	"fmt"
	"testing"

	"github.com/multiversx/mx-chain-simulator-go/config"
	"github.com/multiversx/mx-chain-simulator-go/testscommon"
	"github.com/stretchr/testify/require"
)

func TestCreateBlocksGenerator(t *testing.T) {
	t.Parallel()

	t.Run("disabled auto generate should return disabled component", func(t *testing.T) {
		t.Parallel()

		generator, err := CreateBlocksGenerator(&testscommon.SimulatorHandlerMock{}, config.BlocksGeneratorConfig{})
		require.NoError(t, err)
		require.NotNil(t, generator)
		require.Equal(t, "*disabled.blocksGenerator", fmt.Sprintf("%T", generator))
	})
	t.Run("enabled auto generate should return disabled component", func(t *testing.T) {
		t.Parallel()

		generator, err := CreateBlocksGenerator(&testscommon.SimulatorHandlerMock{}, config.BlocksGeneratorConfig{
			AutoGenerateBlocks: true,
			BlockTimeInMs:      100,
		})
		require.NoError(t, err)
		require.NotNil(t, generator)
		require.Equal(t, "*process.blocksGenerator", fmt.Sprintf("%T", generator))
		generator.Close() // close the internal goroutine
	})
}
