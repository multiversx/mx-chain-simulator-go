package configs

import (
	"errors"
	"os"
	"path"
	"testing"

	"github.com/stretchr/testify/require"

	"github.com/multiversx/mx-chain-simulator-go/testscommon"
)

const (
	mxNodeRepo  = "https://github.com/multiversx/mx-chain-go"
	mxProxyRepo = "https://github.com/multiversx/mx-chain-proxy-go"
	goModUrl    = "../../../go.mod"
)

var expectedErr = errors.New("expected error")

func TestConfigsFetcher(t *testing.T) {
	t.Run("FetchProxyConfigs dir already exists should early exit", func(t *testing.T) {
		cf, _ := NewConfigsFetcher(mxNodeRepo, mxProxyRepo, &testscommon.GitFetcherStub{
			CloneCalled: func(r, d string) error {
				require.Fail(t, "should have not been called")
				return nil
			},
		}, false, goModUrl)

		err := cf.FetchProxyConfigs(t.TempDir()) // directory already exists
		require.Nil(t, err)
	})
	t.Run("FetchProxyConfigs Clone error should error", func(t *testing.T) {
		dir := path.Join(t.TempDir(), "shouldWorkTest")
		cf, _ := NewConfigsFetcher(mxNodeRepo, mxProxyRepo, &testscommon.GitFetcherStub{
			CloneCalled: func(r, d string) error {
				return expectedErr
			},
		}, false, goModUrl)

		err := cf.FetchProxyConfigs(dir)
		require.Equal(t, expectedErr, err)
	})
	t.Run("FetchProxyConfigs Checkout error should error", func(t *testing.T) {
		dir := path.Join(t.TempDir(), "shouldWorkTest")
		cf, _ := NewConfigsFetcher(mxNodeRepo, mxProxyRepo, &testscommon.GitFetcherStub{
			CheckoutCalled: func(repoDir string, commitHashOrBranch string) error {
				return expectedErr
			},
		}, false, goModUrl)

		err := cf.FetchProxyConfigs(dir)
		require.Equal(t, expectedErr, err)
	})
	t.Run("FetchProxyConfigs errors while copying should error", func(t *testing.T) {
		dir := path.Join(t.TempDir(), "shouldWorkTest")
		cf, _ := NewConfigsFetcher(mxNodeRepo, mxProxyRepo, &testscommon.GitFetcherStub{
			CloneCalled: func(r, d string) error {
				return nil
			},
		}, false, goModUrl)

		err := cf.FetchProxyConfigs(dir)
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
		}, false, goModUrl)

		err := cf.FetchProxyConfigs(dir)
		require.Nil(t, err)
	})
	t.Run("FetchNodeConfigs dir already exists should early exit", func(t *testing.T) {
		cf, _ := NewConfigsFetcher(mxNodeRepo, mxProxyRepo, &testscommon.GitFetcherStub{
			CloneCalled: func(r, d string) error {
				require.Fail(t, "should have not been called")
				return nil
			},
		}, false, goModUrl)

		err := cf.FetchNodeConfigs(t.TempDir()) // directory already exists
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
		}, false, goModUrl)

		err := cf.FetchNodeConfigs(dir)
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
		}, true, goModUrl)

		err := cf.FetchNodeConfigs(dir)
		require.Nil(t, err)
	})
}
