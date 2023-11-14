package main

import (
	"errors"
	"fmt"
	"os"
	"os/signal"
	"runtime/debug"
	"syscall"
	"time"

	"github.com/multiversx/mx-chain-core-go/core"
	"github.com/multiversx/mx-chain-core-go/core/check"
	"github.com/multiversx/mx-chain-core-go/core/closing"
	"github.com/multiversx/mx-chain-go/node/chainSimulator"
	"github.com/multiversx/mx-chain-go/node/chainSimulator/components/api"
	logger "github.com/multiversx/mx-chain-logger-go"
	"github.com/multiversx/mx-chain-logger-go/file"
	"github.com/multiversx/mx-chain-simulator-go/config"
	"github.com/multiversx/mx-chain-simulator-go/pkg/facade"
	endpoints "github.com/multiversx/mx-chain-simulator-go/pkg/proxy/api"
	"github.com/multiversx/mx-chain-simulator-go/pkg/proxy/configs"
	"github.com/multiversx/mx-chain-simulator-go/pkg/proxy/creator"
	"github.com/urfave/cli"
)

var (
	log          = logger.GetOrCreate("indexer")
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
		logLevel,
		logSaveFile,
		disableAnsiColor,
		pathToNodeConfigs,
		pathToProxyConfigs,
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
	buildInfo, ok := debug.ReadBuildInfo()
	if !ok {
		return errors.New("cannot read build info")
	}

	cfg, err := loadMainConfig(ctx.GlobalString(configurationFile.Name))
	if err != nil {
		return fmt.Errorf("%w while loading the config file", err)
	}
	fileLogging, err := initializeLogger(ctx, cfg)
	if err != nil {
		return fmt.Errorf("%w while initializing the logger", err)
	}

	configsFetcher, err := configs.NewConfigsFetcher(cfg.Config.Simulator.MxChainRepo, cfg.Config.Simulator.MxProxyRepo)
	if err != nil {
		return err
	}

	nodeConfigs := ctx.GlobalString(pathToNodeConfigs.Name)
	err = configsFetcher.FetchNodeConfigs(buildInfo, nodeConfigs)
	if err != nil {
		return err
	}

	proxyConfigs := ctx.GlobalString(pathToProxyConfigs.Name)
	err = configsFetcher.FetchProxyConfigs(buildInfo, proxyConfigs)
	if err != nil {
		return err
	}

	startTime := time.Now().Unix()
	roundDurationInMillis := uint64(cfg.Config.Simulator.RoundDurationInMs)
	roundsPerEpoch := core.OptionalUint64{
		HasValue: true,
		Value:    uint64(cfg.Config.Simulator.RoundsPerEpoch),
	}

	apiConfigurator := api.NewFreePortAPIConfigurator("localhost")
	simulator, err := chainSimulator.NewChainSimulator(os.TempDir(), uint32(cfg.Config.Simulator.NumOfShards), nodeConfigs, startTime, roundDurationInMillis, roundsPerEpoch, apiConfigurator)
	if err != nil {
		return err
	}

	log.Info("simulators were initialized")

	err = simulator.GenerateBlocks(1)
	if err != nil {
		return err
	}

	metaNode := simulator.GetNodeHandler(core.MetachainShardId)
	restApiInterfaces := simulator.GetRestAPIInterfaces()
	outputProxyConfigs, err := configs.CreateProxyConfigs(configs.ArgsProxyConfigs{
		TemDir:            os.TempDir(),
		PathToProxyConfig: proxyConfigs,
		ServerPort:        cfg.Config.Simulator.ServerPort,
		RestApiInterfaces: restApiInterfaces,
		AddressConverter:  metaNode.GetCoreComponents().AddressPubKeyConverter(),
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

	interrupt := make(chan os.Signal, 1)
	signal.Notify(interrupt, syscall.SIGINT, syscall.SIGTERM)
	<-interrupt

	log.Info("close")
	err = simulator.Close()
	if err != nil {
		log.Warn("cannot close simulator", "error", err)
	}
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

func loadMainConfig(filepath string) (config.Config, error) {
	cfg := config.Config{}
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
