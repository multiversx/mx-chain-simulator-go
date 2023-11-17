package configs

import (
	"runtime/debug"
	"testing"

	"github.com/multiversx/mx-chain-simulator-go/testscommon"
	"github.com/stretchr/testify/require"
)

const (
	mxNodeRepo  = "https://github.com/multiversx/mx-chain-go"
	mxProxyRepo = "https://github.com/multiversx/mx-chain-proxy-go"
)

func TestConfigsFetcher(t *testing.T) {
	dir := t.TempDir()
	cf, _ := NewConfigsFetcher(mxNodeRepo, mxProxyRepo, &testscommon.GitFetcherStub{
		CloneCalled: func(r, d string) error {
			return nil
		},
	})

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
	}, dir)
	require.Nil(t, err)

}
