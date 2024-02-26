package factory

import (
	"github.com/multiversx/mx-chain-simulator-go/config"
	"github.com/multiversx/mx-chain-simulator-go/pkg/process"
	"github.com/multiversx/mx-chain-simulator-go/pkg/process/disabled"
)

// CreateBlocksGenerator creates a new instance of block generator
func CreateBlocksGenerator(simulator process.SimulatorHandler, config config.BlocksGeneratorConfig) (process.BlocksGenerator, error) {
	if config.AutoGenerateBlocks {
		return process.NewBlocksGenerator(process.ArgBlocksGenerator{
			Simulator:     simulator,
			BlockTimeInMs: config.BlockTimeInMs,
		})
	}

	return disabled.NewBlocksGenerator(), nil
}
