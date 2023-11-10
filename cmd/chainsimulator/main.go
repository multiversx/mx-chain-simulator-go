package main

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/multiversx/mx-chain-core-go/core"
	"github.com/multiversx/mx-chain-core-go/core/check"
	"github.com/multiversx/mx-chain-core-go/core/closing"
	"github.com/multiversx/mx-chain-go/node/chainSimulator"
	logger "github.com/multiversx/mx-chain-logger-go"
	"github.com/multiversx/mx-chain-logger-go/file"
	"github.com/multiversx/mx-chain-simulator-go/config"
	"github.com/multiversx/mx-chain-simulator-go/pkg/facade"
	"github.com/multiversx/mx-chain-simulator-go/pkg/proxy"
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

// TODO implement a mechanism that will fetch the config base on the go.mod --> for node and proxy
const (
	pathToNodeConfig  = "../../../mx-chain-go/cmd/node/config"
	pathToProxyConfig = "../../../mx-chain-proxy-go/cmd/proxy/config"
)

func startChainSimulator(ctx *cli.Context) error {
	//buildInfo, ok := debug.ReadBuildInfo()
	//if !ok {
	//	panic("Can't read BuildInfo")
	//}
	//fmt.Println("Dependencies:")
	//for _, dep := range buildInfo.Deps {
	//	fmt.Printf("  %s %s\n", dep.Path, dep.Version)
	//}

	cfg, err := loadMainConfig(ctx.GlobalString(configurationFile.Name))
	if err != nil {
		return fmt.Errorf("%w while loading the config file", err)
	}
	fileLogging, err := initializeLogger(ctx, cfg)
	if err != nil {
		return fmt.Errorf("%w while initializing the logger", err)
	}

	startTime := time.Now().Unix()
	roundDurationInMillis := uint64(6000)
	roundsPerEpoch := core.OptionalUint64{
		HasValue: true,
		Value:    20,
	}

	simulator, err := chainSimulator.NewChainSimulator(os.TempDir(), 3, pathToNodeConfig, startTime, roundDurationInMillis, roundsPerEpoch, true)
	if err != nil {
		return err
	}

	restApiInterfaces := simulator.GetRestAPIInterfaces()
	outputProxyConfigs, err := proxy.CreateProxyConfigs(proxy.ArgsProxyConfigs{
		TemDir:            os.TempDir(),
		PathToProxyConfig: pathToProxyConfig,
		ServerPort:        cfg.Config.ServerPort,
		RestApiInterfaces: restApiInterfaces,
	})
	if err != nil {
		return err
	}

	time.Sleep(time.Second)

	simulatorFacade, err := facade.NewSimulatorFacade(simulator)
	if err != nil {
		return err
	}

	metaNode := simulator.GetNodeHandler(core.MetachainShardId)
	proxyInstance, err := proxy.CreateProxy(proxy.ArgsProxy{
		Config:          outputProxyConfigs.Config,
		NodeHandler:     metaNode,
		PathToConfig:    outputProxyConfigs.PathToTempConfig,
		SimulatorFacade: simulatorFacade,
	})
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
