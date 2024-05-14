package configs

import (
	"testing"

	"github.com/multiversx/mx-chain-go/node/chainSimulator/dtos"
	"github.com/stretchr/testify/require"
)

func createArgsProxyConfigs(t *testing.T) ArgsProxyConfigs {
	return ArgsProxyConfigs{
		TemDir:            t.TempDir(),
		PathToProxyConfig: "testdata",
		ServerPort:        1234,
		RestApiInterfaces: map[uint32]string{
			0: "http://127.0.0.1:8080",
			1: "http://127.0.0.1:8081",
			2: "http://127.0.0.1:8082",
		},
		InitialWallets: map[uint32]*dtos.WalletKey{
			0: {
				Address: dtos.WalletAddress{
					Bech32: "erd17g9splt634xppt782cktfyyfmhdqlya9vqlqjeclpk65ckuxkcwqxu78wy",
				},
				PrivateKeyHex: "NzhkOGI1ZDYxOWVkNzkyY2U5ZWE1YTk5YjZkYjA4NzgwMDA1MzE3OTRlYmVhNzFk\nNWRhYWUwODdlNDE4MGZmZGYyMGIwMGZkN2E4ZDRjMTBhZmM3NTYyY2I0OTA4OWRk\nZGEwZjkzYTU2MDNlMDk2NzFmMGRiNTRjNWI4NmI2MWM=",
			},
		},
	}
}

func TestCreateProxyConfigs(t *testing.T) {
	t.Parallel()

	t.Run("missing proxy config dir should error", func(t *testing.T) {
		args := createArgsProxyConfigs(t)
		args.PathToProxyConfig = "missingDir"
		cfg, err := CreateProxyConfigs(args)
		require.Error(t, err)
		require.Nil(t, cfg)
	})
	t.Run("missing toml should error", func(t *testing.T) {
		args := createArgsProxyConfigs(t)
		args.PathToProxyConfig = t.TempDir()
		cfg, err := CreateProxyConfigs(args)
		require.Error(t, err)
		require.Nil(t, cfg)
	})
	t.Run("should work", func(t *testing.T) {
		cfg, err := CreateProxyConfigs(createArgsProxyConfigs(t))
		require.NoError(t, err)
		require.NotNil(t, cfg)
	})
}
