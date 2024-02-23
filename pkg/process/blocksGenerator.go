package process

import (
	"context"
	"fmt"
	"time"

	"github.com/multiversx/mx-chain-core-go/core/check"
	logger "github.com/multiversx/mx-chain-logger-go"
)

var log = logger.GetOrCreate("process")

const minBlockTimeInMs = 1

// ArgBlocksGenerator defines the dto used to create a new instance of blocksGenerator
type ArgBlocksGenerator struct {
	Simulator     SimulatorHandler
	BlockTimeInMs uint64
}
type blocksGenerator struct {
	cancel    func()
	simulator SimulatorHandler
	blockTime time.Duration
}

// NewBlocksGenerator returns a new instance of blocksGenerator
func NewBlocksGenerator(args ArgBlocksGenerator) (*blocksGenerator, error) {
	if check.IfNil(args.Simulator) {
		return nil, errNilChainSimulator
	}
	if args.BlockTimeInMs < minBlockTimeInMs {
		return nil, fmt.Errorf("%w for BlockTimeInMs, received %d, min expected %d", errInvalidValue, args.BlockTimeInMs, minBlockTimeInMs)
	}
	instance := &blocksGenerator{
		simulator: args.Simulator,
		blockTime: time.Duration(args.BlockTimeInMs) * time.Millisecond,
	}
	var ctx context.Context
	ctx, instance.cancel = context.WithCancel(context.Background())

	go instance.generateBlocks(ctx)

	return instance, nil
}

func (generator *blocksGenerator) generateBlocks(ctx context.Context) {
	log.Info("Running in auto-generate-blocks mode, starting the go routine...")

	timerBlock := time.NewTimer(generator.blockTime)
	for {
		timerBlock.Reset(generator.blockTime)
		select {
		case <-timerBlock.C:
			err := generator.simulator.GenerateBlocks(1)
			if err != nil {
				log.Error("failed to generate block", "error", err.Error())
			}
		case <-ctx.Done():
			log.Debug("closing the automatic blocks generation goroutine...")
			return
		}
	}
}

// Close closes the internal goroutine
func (generator *blocksGenerator) Close() {
	generator.cancel()
}
