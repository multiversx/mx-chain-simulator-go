package main

import (
	"time"

	logger "github.com/multiversx/mx-chain-logger-go"
	"github.com/multiversx/mx-chain-simulator-go/config"
	"github.com/urfave/cli"
)

const nodeOverrideDefaultFilename = "./config/nodeOverrideDefault.toml"

var (
	configurationFile = cli.StringFlag{
		Name:  "config",
		Usage: "The main configuration file to load",
		Value: "./config/config.toml",
	}
	nodeOverrideConfigurationFile = cli.StringFlag{
		Name: "node-override-config",
		Usage: "The node's override configuration file to load. Can define multiple files separated by comma. " +
			"Example: ./config/override1.toml,./config/override2.toml and so on",
		Value: nodeOverrideDefaultFilename,
	}
	logLevel = cli.StringFlag{
		Name: "log-level",
		Usage: "This flag specifies the logger `level(s)`. It can contain multiple comma-separated value. For example" +
			", if set to *:INFO the logs for all packages will have the INFO level. However, if set to *:INFO,api:DEBUG" +
			" the logs for all packages will have the INFO level, excepting the api package which will receive a DEBUG" +
			" log level.",
		Value: "*:" + logger.LogInfo.String(),
	}
	logSaveFile = cli.BoolFlag{
		Name:  "log-save",
		Usage: "Boolean option for enabling log saving. If set, it will automatically save all the logs into a file.",
	}
	// disableAnsiColor defines if the logger subsystem should prevent displaying ANSI colors
	disableAnsiColor = cli.BoolFlag{
		Name:  "disable-ansi-color",
		Usage: "Boolean option for disabling ANSI colors in the logging system.",
	}

	pathToNodeConfigs = cli.StringFlag{
		Name:  "node-configs",
		Usage: "The path to node configs",
		Value: "./config/node/config",
	}
	pathToProxyConfigs = cli.StringFlag{
		Name:  "proxy-configs",
		Usage: "The path to proxy configs",
		Value: "./config/proxy/config",
	}
	startTime = cli.Int64Flag{
		Name:  "start-time",
		Usage: "The start time of the chain",
		Value: time.Now().Unix(),
	}
	roundsPerEpoch = cli.IntFlag{
		Name:  "rounds-per-epoch",
		Usage: "The number of rounds per epoch",
		Value: 20,
	}
	numOfShards = cli.IntFlag{
		Name:  "num-of-shards",
		Usage: "The number of shards",
		Value: 3,
	}
	serverPort = cli.IntFlag{
		Name:  "server-port",
		Usage: "The port of the http server that the proxy component will respond on. If this is set to 0, a random free port will be selected.",
		Value: 8085,
	}
	roundDurationInMs = cli.IntFlag{
		Name:  "round-duration",
		Usage: "The round duration in milliseconds",
		Value: 6000,
	}
	bypassTransactionsSignature = cli.BoolTFlag{
		Name:  "bypass-txs-signature",
		Usage: "This flag is used to bypass the transactions signature verification (by default true)",
	}
	numValidatorsPerShard = cli.IntFlag{
		Name:  "num-validators-per-shard",
		Usage: "This flag is used to specify the number of validators per shard",
		Value: 1,
	}
	numWaitingValidatorsPerShard = cli.IntFlag{
		Name:  "num-waiting-validators-per-shard",
		Usage: "This flag is used to specify the number of waiting validators per shard",
		Value: 0,
	}
	numValidatorsMeta = cli.IntFlag{
		Name:  "num-validators-meta",
		Usage: "This flag is used to specify the number of validators on metachain",
		Value: 1,
	}
	numWaitingValidatorsMeta = cli.IntFlag{
		Name:  "num-waiting-validators-meta",
		Usage: "This flag is used to specify the number of waiting validators on metachain",
		Value: 0,
	}
	initialRound = cli.Uint64Flag{
		Name:  "initial-round",
		Usage: "This flag is used to specify the initial round when chain simulator will start",
		Value: 0,
	}
	initialNonce = cli.Uint64Flag{
		Name:  "initial-nonce",
		Usage: "This flag is used to specify the initial nonce when chain simulator will start",
		Value: 0,
	}
	initialEpoch = cli.UintFlag{
		Name:  "initial-epoch",
		Usage: "This flag is used to specify the initial epoch when chain simulator will start",
		Value: 0,
	}
	autoGenerateBlocks = cli.BoolFlag{
		Name:  "auto-generate-blocks",
		Usage: "Boolean option to specify that blocks should be generated automatically, after a given period of time",
	}
	blockTimeInMs = cli.Uint64Flag{
		Name:  "block-time-in-milliseconds",
		Usage: "The time between blocks generations, when autoGenerateBlocks flag is true",
		Value: 6000,
	}
	skipConfigsDownload = cli.BoolFlag{
		Name:  "skip-configs-download",
		Usage: "The flag is used to specify whether to skip downloading configs",
	}
	fetchConfigsAndClose = cli.BoolFlag{
		Name:  "fetch-configs-and-close",
		Usage: "This flag is used to specify to fetch all configs and close the chain simulator after",
	}
)

func applyFlags(ctx *cli.Context, cfg *config.Config) {
	if ctx.IsSet(roundsPerEpoch.Name) {
		cfg.Config.Simulator.RoundsPerEpoch = ctx.GlobalInt(roundsPerEpoch.Name)
	}

	if ctx.IsSet(numOfShards.Name) {
		cfg.Config.Simulator.NumOfShards = ctx.GlobalInt(numOfShards.Name)
	}

	if ctx.IsSet(serverPort.Name) {
		cfg.Config.Simulator.ServerPort = ctx.GlobalInt(serverPort.Name)
	}

	if ctx.IsSet(roundDurationInMs.Name) {
		cfg.Config.Simulator.RoundDurationInMs = ctx.GlobalInt(roundDurationInMs.Name)
	}

	if ctx.IsSet(initialRound.Name) {
		cfg.Config.Simulator.InitialRound = ctx.GlobalInt64(initialRound.Name)
	}

	if ctx.IsSet(initialNonce.Name) {
		cfg.Config.Simulator.InitialNonce = ctx.GlobalUint64(initialNonce.Name)
	}

	if ctx.IsSet(initialEpoch.Name) {
		cfg.Config.Simulator.InitialEpoch = uint32(ctx.GlobalUint(initialEpoch.Name))
	}

	if ctx.IsSet(autoGenerateBlocks.Name) {
		cfg.Config.BlocksGenerator.AutoGenerateBlocks = ctx.GlobalBool(autoGenerateBlocks.Name)
	}

	if ctx.IsSet(blockTimeInMs.Name) {
		cfg.Config.BlocksGenerator.BlockTimeInMs = ctx.GlobalUint64(blockTimeInMs.Name)
	}
}
