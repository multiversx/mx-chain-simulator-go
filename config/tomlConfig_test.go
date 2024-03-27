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
# Test comment
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
