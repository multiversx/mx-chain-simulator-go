package config

import (
	"github.com/multiversx/mx-chain-core-go/core"
)

type overrideConfigsHandler struct {
}

// NewOverrideConfigsHandler creates a new instance of type overrideConfigsHandler
func NewOverrideConfigsHandler() *overrideConfigsHandler {
	return &overrideConfigsHandler{}
}

// ReadAll will read the configs from all provided files and merge all read data
func (handler *overrideConfigsHandler) ReadAll(filenames ...string) (OverrideConfigs, error) {
	mergedConfigs := OverrideConfigs{}
	for _, filename := range filenames {
		readConfigs := OverrideConfigs{}
		err := core.LoadTomlFile(&readConfigs, filename)
		if err != nil {
			return OverrideConfigs{}, err
		}

		mergedConfigs.OverridableConfigTomlValues = append(mergedConfigs.OverridableConfigTomlValues, readConfigs.OverridableConfigTomlValues...)
	}

	return mergedConfigs, nil
}
