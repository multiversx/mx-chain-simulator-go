package main

import (
	"errors"
	"fmt"
	"os"
	"os/signal"
	"runtime/debug"
	"strconv"
	"syscall"
	"time"

	"github.com/multiversx/mx-chain-core-go/core"
	"github.com/multiversx/mx-chain-core-go/core/check"
	"github.com/multiversx/mx-chain-core-go/core/closing"
	nodeConfig "github.com/multiversx/mx-chain-go/config"
	"github.com/multiversx/mx-chain-go/config/overridableConfig"
	"github.com/multiversx/mx-chain-go/node/chainSimulator"
	"github.com/multiversx/mx-chain-go/node/chainSimulator/components/api"
	logger "github.com/multiversx/mx-chain-logger-go"
	"github.com/multiversx/mx-chain-logger-go/file"
	"github.com/multiversx/mx-chain-simulator-go/config"
	"github.com/multiversx/mx-chain-simulator-go/pkg/facade"
	"github.com/multiversx/mx-chain-simulator-go/pkg/factory"
	endpoints "github.com/multiversx/mx-chain-simulator-go/pkg/proxy/api"
	"github.com/multiversx/mx-chain-simulator-go/pkg/proxy/configs"
	"github.com/multiversx/mx-chain-simulator-go/pkg/proxy/configs/git"
	"github.com/multiversx/mx-chain-simulator-go/pkg/proxy/creator"
	"github.com/urfave/cli"
)

const timeToAllowProxyToStart = time.Millisecond * 10

var (
	log          = logger.GetOrCreate("chainsimulator")
	helpTemplate = `NAME:
   {{.Name}} - {{.Usage}}
USAGE:
   {{.HelpName}} {{if .VisibleFlags}}[global options]{{end}}
   {{if len .Authors}}
AUTHOR:
   {{range .Authors}}{{ . }}{{end}}
   {{end}}{{if .Commands}}
GLOBAL OPTIONS:
   {{range .VisibleFlags}}{{.}}
   {{end}}
VERSION:
   {{.Version}}
   {{end}}
`
)

func main() {
	app := cli.NewApp()
	cli.AppHelpTemplate = helpTemplate
	app.Name = "Chain Simulator"
	app.Usage = ""
	app.Flags = []cli.Flag{
		configurationFile,
		nodeOverrideConfigurationFile,
		logLevel,
		logSaveFile,
		disableAnsiColor,
		pathToNodeConfigs,
		pathToProxyConfigs,
		startTime,
		roundsPerEpoch,
		numOfShards,
		serverPort,
		roundDurationInMs,
		bypassTransactionsSignature,
		numValidatorsPerShard,
		numWaitingValidatorsPerShard,
		numValidatorsMeta,
		numWaitingValidatorsMeta,
		initialRound,
		initialNonce,
		initialEpoch,
		autoGenerateBlocks,
		blockTimeInMs,
		skipConfigsDownload,
	}

	app.Authors = []cli.Author{
		{
			Name:  "The MultiversX Team",
			Email: "contact@multiversx.com",
		},
	}

	app.Action = startChainSimulator

	err := app.Run(os.Args)
	if err != nil {
		log.Error(err.Error())
		os.Exit(1)
	}
}

func startChainSimulator(ctx *cli.Context) error {
	cfg, err := loadMainConfig(ctx.GlobalString(configurationFile.Name))
	if err != nil {
		return fmt.Errorf("%w while loading the config file", err)
	}

	overrideCfg, err := loadOverrideConfig(ctx.GlobalString(nodeOverrideConfigurationFile.Name))
	if err != nil {
		return fmt.Errorf("%w while loading the node override config file", err)
	}

	applyFlags(ctx, &cfg)

	fileLogging, err := initializeLogger(ctx, cfg)
	if err != nil {
		return fmt.Errorf("%w while initializing the logger", err)
	}

	skipDownload := ctx.GlobalBool(skipConfigsDownload.Name)
	nodeConfigs := ctx.GlobalString(pathToNodeConfigs.Name)
	proxyConfigs := ctx.GlobalString(pathToProxyConfigs.Name)
	err = fetchConfigs(skipDownload, cfg, nodeConfigs, proxyConfigs)
	if err != nil {
		return fmt.Errorf("%w while fetching configs", err)
	}

	bypassTxsSignature := ctx.GlobalBool(bypassTransactionsSignature.Name)
	log.Warn("signature", "bypass", bypassTxsSignature)
	roundDurationInMillis := uint64(cfg.Config.Simulator.RoundDurationInMs)
	rounds := core.OptionalUint64{
		HasValue: true,
		Value:    uint64(cfg.Config.Simulator.RoundsPerEpoch),
	}

	numValidatorsShard := ctx.GlobalInt(numValidatorsPerShard.Name)
	if numValidatorsShard < 1 {
		return errors.New("invalid value for the number of validators per shard")
	}
	numWaitingValidatorsShard := ctx.GlobalInt(numWaitingValidatorsPerShard.Name)
	if numWaitingValidatorsShard < 0 {
		return errors.New("invalid value for the number of waiting validators per shard")
	}

	numValidatorsMetaShard := ctx.GlobalInt(numValidatorsMeta.Name)
	if numValidatorsMetaShard < 1 {
		return errors.New("invalid value for the number of validators for metachain")
	}
	numWaitingValidatorsMetaShard := ctx.GlobalInt(numWaitingValidatorsMeta.Name)
	if numWaitingValidatorsMetaShard < 0 {
		return errors.New("invalid value for the number of waiting validators for metachain")
	}

	localRestApiInterface := "localhost"
	apiConfigurator := api.NewFreePortAPIConfigurator(localRestApiInterface)
	proxyPort := cfg.Config.Simulator.ServerPort
	proxyURL := fmt.Sprintf("%s:%d", localRestApiInterface, proxyPort)
	if proxyPort == 0 {
		proxyURL = apiConfigurator.RestApiInterface(0)
		portString := proxyURL[len(localRestApiInterface)+1:]
		port, errConvert := strconv.Atoi(portString)
		if errConvert != nil {
			return fmt.Errorf("internal error while searching a free port for the proxy component: %w", errConvert)
		}
		proxyPort = port
	}

	startTimeUnix := ctx.GlobalInt64(startTime.Name)

	tempDir, err := os.MkdirTemp(os.TempDir(), "")
	if err != nil {
		return err
	}

	var alterConfigsError error
	argsChainSimulator := chainSimulator.ArgsChainSimulator{
		BypassTxSignatureCheck:   bypassTxsSignature,
		TempDir:                  tempDir,
		PathToInitialConfig:      nodeConfigs,
		NumOfShards:              uint32(cfg.Config.Simulator.NumOfShards),
		GenesisTimestamp:         startTimeUnix,
		RoundDurationInMillis:    roundDurationInMillis,
		RoundsPerEpoch:           rounds,
		ApiInterface:             apiConfigurator,
		MinNodesPerShard:         uint32(numValidatorsShard),
		NumNodesWaitingListShard: uint32(numWaitingValidatorsShard),
		MetaChainMinNodes:        uint32(numValidatorsMetaShard),
		NumNodesWaitingListMeta:  uint32(numWaitingValidatorsMetaShard),
		InitialRound:             cfg.Config.Simulator.InitialRound,
		InitialNonce:             cfg.Config.Simulator.InitialNonce,
		InitialEpoch:             cfg.Config.Simulator.InitialEpoch,
		AlterConfigsFunction: func(cfg *nodeConfig.Configs) {
			alterConfigsError = overridableConfig.OverrideConfigValues(overrideCfg.OverridableConfigTomlValues, cfg)
		},
	}
	simulator, err := chainSimulator.NewChainSimulator(argsChainSimulator)
	if err != nil {
		return err
	}

	if alterConfigsError != nil {
		return alterConfigsError
	}

	log.Info("simulators were initialized")

	err = simulator.GenerateBlocks(1)
	if err != nil {
		return err
	}

	generator, err := factory.CreateBlocksGenerator(simulator, cfg.Config.BlocksGenerator)
	if err != nil {
		return err
	}

	metaNode := simulator.GetNodeHandler(core.MetachainShardId)
	restApiInterfaces := simulator.GetRestAPIInterfaces()
	outputProxyConfigs, err := configs.CreateProxyConfigs(configs.ArgsProxyConfigs{
		TemDir:            tempDir,
		PathToProxyConfig: proxyConfigs,
		ServerPort:        proxyPort,
		RestApiInterfaces: restApiInterfaces,
		InitialWallets:    simulator.GetInitialWalletKeys().BalanceWallets,
	})
	if err != nil {
		return err
	}

	time.Sleep(time.Second)

	proxyInstance, err := creator.CreateProxy(creator.ArgsProxy{
		Config:        outputProxyConfigs.Config,
		NodeHandler:   metaNode,
		PathToConfig:  outputProxyConfigs.PathToTempConfig,
		PathToPemFile: outputProxyConfigs.PathToPemFile,
	})
	if err != nil {
		return err
	}

	simulatorFacade, err := facade.NewSimulatorFacade(simulator)
	if err != nil {
		return err
	}

	endpointsProc, err := endpoints.NewEndpointsProcessor(simulatorFacade)
	if err != nil {
		return err
	}

	err = endpointsProc.ExtendProxyServer(proxyInstance.GetHttpServer())
	if err != nil {
		return err
	}

	proxyInstance.Start()

	time.Sleep(timeToAllowProxyToStart)
	log.Info(fmt.Sprintf("chain simulator's is accessible through the URL %s", proxyURL))

	interrupt := make(chan os.Signal, 1)
	signal.Notify(interrupt, syscall.SIGINT, syscall.SIGTERM)
	<-interrupt

	log.Info("close")

	generator.Close()

	simulator.Close()
	proxyInstance.Close()

	if !check.IfNilReflect(fileLogging) {
		err = fileLogging.Close()
		log.LogIfError(err)
	}

	return nil
}

func initializeLogger(ctx *cli.Context, cfg config.Config) (closing.Closer, error) {
	logLevelFlagValue := ctx.GlobalString(logLevel.Name)
	err := logger.SetLogLevel(logLevelFlagValue)
	if err != nil {
		return nil, err
	}

	withLogFile := ctx.GlobalBool(logSaveFile.Name)
	if !withLogFile {
		return nil, nil
	}

	workingDir, err := os.Getwd()
	if err != nil {
		log.LogIfError(err)
		workingDir = ""
	}

	fileLogging, err := file.NewFileLogging(file.ArgsFileLogging{
		WorkingDir:      workingDir,
		DefaultLogsPath: cfg.Config.Logs.LogsPath,
		LogFilePrefix:   cfg.Config.Logs.LogFilePrefix,
	})
	if err != nil {
		return nil, fmt.Errorf("%w creating a log file", err)
	}

	err = fileLogging.ChangeFileLifeSpan(
		time.Second*time.Duration(cfg.Config.Logs.LogFileLifeSpanInSec),
		uint64(cfg.Config.Logs.LogFileLifeSpanInMB),
	)
	if err != nil {
		return nil, err
	}

	disableAnsi := ctx.GlobalBool(disableAnsiColor.Name)
	err = removeANSIColorsForLoggerIfNeeded(disableAnsi)
	if err != nil {
		return nil, err
	}

	return fileLogging, nil
}

func fetchConfigs(skipDownload bool, cfg config.Config, nodeConfigs, proxyConfigs string) error {
	buildInfo, ok := debug.ReadBuildInfo()
	if !ok {
		return errors.New("cannot read build info")
	}
	if skipDownload {
		log.Warn(`flag "skip-configs-download" has been provided, if configs for node and proxy are missing simulator will not start`)
		return nil
	}

	gitFetcher := git.NewGitFetcher()
	configsFetcher, err := configs.NewConfigsFetcher(cfg.Config.Simulator.MxChainRepo, cfg.Config.Simulator.MxProxyRepo, gitFetcher)
	if err != nil {
		return err
	}

	err = configsFetcher.FetchNodeConfigs(buildInfo, nodeConfigs)
	if err != nil {
		return err
	}

	err = configsFetcher.FetchProxyConfigs(buildInfo, proxyConfigs)
	if err != nil {
		return err
	}

	return nil
}

func loadMainConfig(filepath string) (config.Config, error) {
	cfg := config.Config{}
	err := core.LoadTomlFile(&cfg, filepath)

	return cfg, err
}

func loadOverrideConfig(filepath string) (config.OverrideConfigs, error) {
	cfg := config.OverrideConfigs{}
	err := core.LoadTomlFile(&cfg, filepath)

	return cfg, err
}

func removeANSIColorsForLoggerIfNeeded(disableAnsi bool) error {
	if !disableAnsi {
		return nil
	}

	err := logger.RemoveLogObserver(os.Stdout)
	if err != nil {
		return err
	}

	return logger.AddLogObserver(os.Stdout, &logger.PlainFormatter{})
}
