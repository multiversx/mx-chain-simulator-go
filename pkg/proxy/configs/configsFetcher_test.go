package configs

import (
	"os"
	"runtime/debug"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestConfigsFetcher(t *testing.T) {
	cf, _ := NewConfigsFetcher()
	debug.ReadBuildInfo()

	defer func() {
		_ = os.RemoveAll("./test")
	}()

	err := cf.FetchProxyConfigs(&debug.BuildInfo{
		Deps: []*debug.Module{
			{
				Path:    "github.com/multiversx/mx-chain-go",
				Version: "v1.6.4-0.20231113110318-c71f3fc323f4",
			},
			{
				Path:    "github.com/multiversx/mx-chain-proxy-go",
				Version: "v1.1.41",
			},
		},
	}, "./test")
	require.Nil(t, err)

}
