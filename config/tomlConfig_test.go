package config

import (
	"testing"

	"github.com/multiversx/mx-chain-go/config"
	"github.com/pelletier/go-toml"
	"github.com/stretchr/testify/assert"
)

func TestLoadNodeOverrideConfigs(t *testing.T) {
	t.Parallel()

	testString := `
# OverridableConfigTomlValues represents an array of items to be overloaded inside other configuration files, which can be helpful
# so that certain config values need to remain the same during upgrades.
# (for example, an Elasticsearch user wants external.toml->ElasticSearchConnector.Enabled to remain true all the time during upgrades, while the default
# configuration of the node has the false value)
# The Path indicates what value to change, while Value represents the new value in string format. The node operator must make sure
# to follow the same type of the original value (ex: uint32: "37", float32: "37.0", bool: "true")
# File represents the file name that holds the configuration. Currently, the supported files are:
# api.toml, config.toml, economics.toml, enableEpochs.toml, enableRounds.toml, external.toml, fullArchiveP2P.toml, p2p.toml, ratings.toml, systemSmartContractsConfig.toml
# -------------------------------
# Un-comment and update the following section in order to enable config values overloading
# -------------------------------
OverridableConfigTomlValues = [
    { File = "config.toml", Path = "A", Value = "B" },
    { File = "external.toml", Path = "C", Value = "D" }
]
`

	expectedConfig := OverrideConfigs{
		OverridableConfigTomlValues: []config.OverridableConfig{
			{
				File:  "config.toml",
				Path:  "A",
				Value: "B",
			},
			{
				File:  "external.toml",
				Path:  "C",
				Value: "D",
			},
		},
	}

	cfg := OverrideConfigs{}

	err := toml.Unmarshal([]byte(testString), &cfg)
	assert.Nil(t, err)
	assert.Equal(t, expectedConfig, cfg)
}
