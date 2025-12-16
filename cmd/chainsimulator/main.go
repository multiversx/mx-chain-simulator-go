package main

import (
	"errors"
	"fmt"
	"os"
	"os/signal"
	"runtime/debug"
	"strconv"
	"strings"
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
	"github.com/urfave/cli"

	"github.com/multiversx/mx-chain-simulator-go/config"
	"github.com/multiversx/mx-chain-simulator-go/pkg/facade"
	"github.com/multiversx/mx-chain-simulator-go/pkg/factory"
	endpoints "github.com/multiversx/mx-chain-simulator-go/pkg/proxy/api"
	"github.com/multiversx/mx-chain-simulator-go/pkg/proxy/configs"
	"github.com/multiversx/mx-chain-simulator-go/pkg/proxy/configs/git"
	"github.com/multiversx/mx-chain-simulator-go/pkg/proxy/creator"
)

const timeToAllowProxyToStart = time.Millisecond * 10
const overrideConfigFilesSeparator = ","
const tempDirPattern = "mx-chainsimulator-*"

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
		supernovaRoundsPerEpoch,
		numOfShards,
		serverPort,
		roundDurationInMs,
		supernovaRoundDurationInMs,
		bypassTransactionsSignature,
		bypassBlocksSignature,
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
		fetchConfigsAndClose,
		pathWhereToSaveLogs,
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

	overrideConfigsHandler := config.NewOverrideConfigsHandler()
	overrideFiles := determineOverrideConfigFiles(ctx)
	log.Info("using the override config files", "files", overrideFiles)
	overrideCfg, err := overrideConfigsHandler.ReadAll(overrideFiles...)
	if err != nil {
		return fmt.Errorf("%w while loading the node override config files", err)
	}

	applyFlags(ctx, &cfg)

	fileLogging, err := initializeLogger(ctx, cfg)
	if err != nil {
		return fmt.Errorf("%w while initializing the logger", err)
	}

	skipDownload := ctx.GlobalBool(skipConfigsDownload.Name)
	nodeConfigs := ctx.GlobalString(pathToNodeConfigs.Name)
	proxyConfigs := ctx.GlobalString(pathToProxyConfigs.Name)
	fetchConfigsAndCloseBool := ctx.GlobalBool(fetchConfigsAndClose.Name)
	err = fetchConfigs(skipDownload, cfg, nodeConfigs, proxyConfigs)
	if err != nil {
		return fmt.Errorf("%w while fetching configs", err)
	}
	if fetchConfigsAndCloseBool {
		return nil
	}

	bypassTxsSignature := ctx.GlobalBool(bypassTransactionsSignature.Name)
	log.Debug("signature", "bypass", bypassTxsSignature)
	bypassBlocksSignature := ctx.GlobalBool(bypassBlocksSignature.Name)
	log.Debug("blocks", "bypass", bypassBlocksSignature)
	roundDurationInMillis := uint64(cfg.Config.Simulator.RoundDurationInMs)
	supernovaRoundDurationInMillis := uint64(cfg.Config.Simulator.SupernovaRoundDurationInMs)
	rounds := core.OptionalUint64{
		HasValue: true,
		Value:    uint64(cfg.Config.Simulator.RoundsPerEpoch),
	}
	supernovaRounds := core.OptionalUint64{
		HasValue: true,
		Value:    uint64(cfg.Config.Simulator.SupernovaRoundsPerEpoch),
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
	startTimeUnix := ctx.GlobalInt64(startTime.Name)

	tempDir, err := os.MkdirTemp(os.TempDir(), tempDirPattern)
	if err != nil {
		return err
	}

	var alterConfigsError error
	argsChainSimulator := chainSimulator.ArgsChainSimulator{
		BypassTxSignatureCheck:         bypassTxsSignature,
		BypassBlockSignatureCheck:      bypassBlocksSignature,
		TempDir:                        tempDir,
		PathToInitialConfig:            nodeConfigs,
		NumOfShards:                    uint32(cfg.Config.Simulator.NumOfShards),
		GenesisTimestamp:               startTimeUnix,
		RoundDurationInMillis:          roundDurationInMillis,
		SupernovaRoundDurationInMillis: supernovaRoundDurationInMillis,
		RoundsPerEpoch:                 rounds,
		SupernovaRoundsPerEpoch:        supernovaRounds,
		ApiInterface:                   apiConfigurator,
		MinNodesPerShard:               uint32(numValidatorsShard),
		NumNodesWaitingListShard:       uint32(numWaitingValidatorsShard),
		MetaChainMinNodes:              uint32(numValidatorsMetaShard),
		NumNodesWaitingListMeta:        uint32(numWaitingValidatorsMetaShard),
		InitialRound:                   cfg.Config.Simulator.InitialRound,
		InitialNonce:                   cfg.Config.Simulator.InitialNonce,
		InitialEpoch:                   cfg.Config.Simulator.InitialEpoch,
		AlterConfigsFunction: func(cfg *nodeConfig.Configs) {
			alterConfigsError = overridableConfig.OverrideConfigValues(overrideCfg.OverridableConfigTomlValues, cfg)
		},
		VmQueryDelayAfterStartInMs: 0,
	}
	simulator, err := chainSimulator.NewChainSimulator(argsChainSimulator)
	if err != nil {
		return err
	}

	if alterConfigsError != nil {
		return alterConfigsError
	}

	log.Info("simulators were initialized")

	for shardID := uint32(0); shardID < uint32(cfg.Config.Simulator.NumOfShards); shardID++ {
		err = simulator.GetNodeHandler(shardID).SetKeyValueForAddress(core.SystemAccountAddress, make(map[string]string))
		if err != nil {
			return err
		}
	}

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
		RestApiInterfaces: restApiInterfaces,
		InitialWallets:    simulator.GetInitialWalletKeys().BalanceWallets,
	})
	if err != nil {
		return err
	}

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

	outputProxyConfigs.Config.GeneralSettings.ServerPort = proxyPort
	outputProxy, err := creator.CreateProxy(creator.ArgsProxy{
		Config:         outputProxyConfigs.Config,
		NodeHandler:    metaNode,
		PathToConfig:   outputProxyConfigs.PathToTempConfig,
		PathToPemFile:  outputProxyConfigs.PathToPemFile,
		NumberOfShards: uint32(cfg.Config.Simulator.NumOfShards),
	})
	if err != nil {
		return err
	}

	proxyInstance := outputProxy.ProxyHandler

	simulatorFacade, err := facade.NewSimulatorFacade(simulator, outputProxy.ProxyTransactionHandler)
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

	pathLogsSave := ctx.GlobalString(pathWhereToSaveLogs.Name)
	fileLogging, err := file.NewFileLogging(file.ArgsFileLogging{
		WorkingDir:      pathLogsSave,
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
		log.Warn(`flag "skip-configs-download" has been provided, if the configs are missing, then simulator will not start`)
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

	return configsFetcher.FetchProxyConfigs(buildInfo, proxyConfigs)
}

func loadMainConfig(filepath string) (config.Config, error) {
	cfg := config.Config{}
	err := core.LoadTomlFile(&cfg, filepath)

	return cfg, err
}

func determineOverrideConfigFiles(ctx *cli.Context) []string {
	overrideFiles := strings.Split(ctx.GlobalString(nodeOverrideConfigurationFile.Name), overrideConfigFilesSeparator)

	for _, filename := range overrideFiles {
		if strings.Contains(filename, nodeOverrideDefaultFilename) {
			return overrideFiles
		}
	}

	return append([]string{nodeOverrideDefaultPath}, overrideFiles...)
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
