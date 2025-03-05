package configs

import (
	"errors"
	"os"
	"path"
	"runtime/debug"
	"testing"

	"github.com/stretchr/testify/require"

	"github.com/multiversx/mx-chain-simulator-go/testscommon"
)

const (
	mxNodeRepo  = "https://github.com/multiversx/mx-chain-go"
	mxProxyRepo = "https://github.com/multiversx/mx-chain-proxy-go"
)

var expectedErr = errors.New("expected error")

func TestConfigsFetcher(t *testing.T) {
	t.Run("FetchProxyConfigs dir already exists should early exit", func(t *testing.T) {
		cf, _ := NewConfigsFetcher(mxNodeRepo, mxProxyRepo, &testscommon.GitFetcherStub{
			CloneCalled: func(r, d string) error {
				require.Fail(t, "should have not been called")
				return nil
			},
		}, false)

		err := cf.FetchProxyConfigs(&debug.BuildInfo{
			Deps: []*debug.Module{
				{
					Path:    "github.com/multiversx/mx-chain-proxy-go",
					Version: "v1.1.41",
				},
			},
		}, t.TempDir()) // directory already exists
		require.Nil(t, err)
	})
	t.Run("FetchProxyConfigs Clone error should error", func(t *testing.T) {
		dir := path.Join(t.TempDir(), "shouldWorkTest")
		cf, _ := NewConfigsFetcher(mxNodeRepo, mxProxyRepo, &testscommon.GitFetcherStub{
			CloneCalled: func(r, d string) error {
				return expectedErr
			},
		}, false)

		err := cf.FetchProxyConfigs(&debug.BuildInfo{
			Deps: []*debug.Module{
				{
					Path:    "github.com/multiversx/mx-chain-proxy-go",
					Version: "v1.1.41",
				},
			},
		}, dir)
		require.Equal(t, expectedErr, err)
	})
	t.Run("FetchProxyConfigs Checkout error should error", func(t *testing.T) {
		dir := path.Join(t.TempDir(), "shouldWorkTest")
		cf, _ := NewConfigsFetcher(mxNodeRepo, mxProxyRepo, &testscommon.GitFetcherStub{
			CheckoutCalled: func(repoDir string, commitHashOrBranch string) error {
				return expectedErr
			},
		}, false)

		err := cf.FetchProxyConfigs(&debug.BuildInfo{
			Deps: []*debug.Module{
				{
					Path:    "github.com/multiversx/mx-chain-proxy-go",
					Version: "v1.1.41",
				},
			},
		}, dir)
		require.Equal(t, expectedErr, err)
	})
	t.Run("FetchProxyConfigs errors while copying should error", func(t *testing.T) {
		dir := path.Join(t.TempDir(), "shouldWorkTest")
		cf, _ := NewConfigsFetcher(mxNodeRepo, mxProxyRepo, &testscommon.GitFetcherStub{
			CloneCalled: func(r, d string) error {
				return nil
			},
		}, false)

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
		require.Error(t, err)
	})
	t.Run("FetchProxyConfigs should work", func(t *testing.T) {
		dir := path.Join(t.TempDir(), "shouldWorkTest")
		cf, _ := NewConfigsFetcher(mxNodeRepo, mxProxyRepo, &testscommon.GitFetcherStub{
			CloneCalled: func(r, d string) error {
				err := os.MkdirAll(path.Join(os.TempDir(), "repo/cmd/proxy/config"), os.ModePerm)
				require.NoError(t, err)

				return nil
			},
		}, false)

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
	})
	t.Run("FetchNodeConfigs dir already exists should early exit", func(t *testing.T) {
		cf, _ := NewConfigsFetcher(mxNodeRepo, mxProxyRepo, &testscommon.GitFetcherStub{
			CloneCalled: func(r, d string) error {
				require.Fail(t, "should have not been called")
				return nil
			},
		}, false)

		err := cf.FetchNodeConfigs(&debug.BuildInfo{
			Deps: []*debug.Module{
				{
					Path:    "github.com/multiversx/mx-chain-go",
					Version: "v1.6.4-0.20231113110318-c71f3fc323f4",
				},
			},
		}, t.TempDir()) // directory already exists
		require.Nil(t, err)
	})
	t.Run("FetchNodeConfigs should work", func(t *testing.T) {
		dir := path.Join(t.TempDir(), "shouldWorkTest")
		cf, _ := NewConfigsFetcher(mxNodeRepo, mxProxyRepo, &testscommon.GitFetcherStub{
			CloneCalled: func(r, d string) error {
				err := os.MkdirAll(path.Join(os.TempDir(), "repo/cmd/node/config"), os.ModePerm)
				require.NoError(t, err)

				return nil
			},
		}, false)

		err := cf.FetchNodeConfigs(&debug.BuildInfo{
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
	})
	t.Run("FetchNodeConfigs for sovereign should work", func(t *testing.T) {
		dir := path.Join(t.TempDir(), "shouldWorkTest")
		cf, _ := NewConfigsFetcher(mxNodeRepo, mxProxyRepo, &testscommon.GitFetcherStub{
			CloneCalled: func(r, d string) error {
				err := os.MkdirAll(path.Join(os.TempDir(), "repo/cmd/node/config"), os.ModePerm)
				require.NoError(t, err)
				err = os.MkdirAll(path.Join(os.TempDir(), "repo/cmd/sovereignnode/config"), os.ModePerm)
				require.NoError(t, err)

				return nil
			},
		}, true)

		err := cf.FetchNodeConfigs(&debug.BuildInfo{
			Deps: []*debug.Module{
				{
					Path:    "github.com/multiversx/mx-chain-go",
					Version: "v1.8.10-0.20250206083958-e89ab5d17dc5",
				},
				{
					Path:    "github.com/multiversx/mx-chain-proxy-go",
					Version: "v1.1.58-0.20250131123034-f4bca654667d",
				},
			},
		}, dir)
		require.Nil(t, err)
	})
}
