package config

import (
	"testing"

	"github.com/multiversx/mx-chain-go/config"
	"github.com/stretchr/testify/assert"
)

func TestNewOverrideConfigsHandler(t *testing.T) {
	t.Parallel()

	// test

	handler := NewOverrideConfigsHandler()
	assert.NotNil(t, handler)
}

func TestOverrideConfigsHandler_ReadAll(t *testing.T) {
	t.Parallel()

	t.Run("should error if it can not find a file", func(t *testing.T) {
		t.Parallel()

		handler := NewOverrideConfigsHandler()
		readConfig, err := handler.ReadAll("./testdata/override1.toml", "file-not-found")
		assert.NotNil(t, err)
		assert.Contains(t, err.Error(), "/file-not-found")
		assert.Equal(t, OverrideConfigs{}, readConfig)
	})
	t.Run("should work with 3 files", func(t *testing.T) {
		t.Parallel()

		handler := NewOverrideConfigsHandler()
		readConfig, err := handler.ReadAll("./testdata/override1.toml",
			"./testdata/override2.toml",
			"./testdata/override3.toml")
		assert.Nil(t, err)

		expectedConfig := OverrideConfigs{
			OverridableConfigTomlValues: []config.OverridableConfig{
				{
					File:  "systemSmartContractsConfig.toml",
					Path:  "StakingSystemSCConfig.NodeLimitPercentage",
					Value: "1.0",
				},
				{
					File:  "config.toml",
					Path:  "MiniBlocksStorage.Cache.Name",
					Value: "MiniBlocksStorage",
				},
				{
					File:  "external.toml",
					Path:  "ElasticSearchConnector.Enabled",
					Value: "true",
				},
				{
					File:  "external.toml",
					Path:  "ElasticSearchConnector.Enabled",
					Value: "false",
				},
			},
		}

		assert.Equal(t, expectedConfig, readConfig)
	})
}
