package disabled

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestBlocksGenerator(t *testing.T) {
	t.Parallel()

	generator := NewBlocksGenerator()
	require.NotNil(t, generator)
	generator.Close()
}
