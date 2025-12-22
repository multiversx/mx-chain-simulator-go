package creator

import (
	"context"
	"errors"
	"math/big"
	"net/http"
	"path"
	"time"

	"github.com/multiversx/mx-chain-go/node/chainSimulator/process"
	logger "github.com/multiversx/mx-chain-logger-go"
	"github.com/multiversx/mx-chain-proxy-go/api"
	"github.com/multiversx/mx-chain-proxy-go/common"
	"github.com/multiversx/mx-chain-proxy-go/config"
	"github.com/multiversx/mx-chain-proxy-go/data"
	"github.com/multiversx/mx-chain-proxy-go/metrics"
	"github.com/multiversx/mx-chain-proxy-go/observer"
	processProxy "github.com/multiversx/mx-chain-proxy-go/process"
	"github.com/multiversx/mx-chain-proxy-go/process/cache"
	processFactory "github.com/multiversx/mx-chain-proxy-go/process/factory"
	versionsFactory "github.com/multiversx/mx-chain-proxy-go/versions/factory"
	proxy2 "github.com/multiversx/mx-chain-simulator-go/pkg/proxy"
	"github.com/multiversx/mx-chain-storage-go/timecache"
)

var log = logger.GetOrCreate("proxy")

// ArgsProxy holds the arguments needed to create a new instance of proxy
type ArgsProxy struct {
	PathToConfig   string
	PathToPemFile  string
	Config         *config.Config
	NodeHandler    process.NodeHandler
	NumberOfShards uint32
}

// ArgsOutputProxy the components that are returned by proxy creator
type ArgsOutputProxy struct {
	ProxyHandler            proxy2.ProxyHandler
	ProxyTransactionHandler proxy2.ProxyTransactionsHandler
}

type proxy struct {
	closableComponents *data.ClosableComponentsHandler
	httpServer         *http.Server
}

// CreateProxy will create a new instance of proxy
func CreateProxy(args ArgsProxy) (*ArgsOutputProxy, error) {
	proxyInstance := &proxy{
		closableComponents: data.NewClosableComponentsHandler(),
	}

	statusMetricsProvider := metrics.NewStatusMetrics()

	nodesProviderFactory, err := observer.NewNodesProviderFactory(*args.Config, "", args.NumberOfShards)
	if err != nil {
		return nil, err
	}
	observersProvider, err := nodesProviderFactory.CreateObservers()
	if err != nil {
		return nil, err
	}
	fullHistoryNodesProvider, err := nodesProviderFactory.CreateFullHistoryNodes()
	if err != nil {
		if !errors.Is(err, observer.ErrEmptyObserversList) {
			return nil, err
		}
	}

	pubKeyConverter := args.NodeHandler.GetCoreComponents().AddressPubKeyConverter()
	shardCoord := args.NodeHandler.GetShardCoordinator()
	bp, err := processProxy.NewBaseProcessor(
		args.Config.GeneralSettings.RequestTimeoutSec,
		shardCoord,
		observersProvider,
		fullHistoryNodesProvider,
		pubKeyConverter,
		false,
	)
	if err != nil {
		return nil, err
	}
	bp.StartNodesSyncStateChecks()

	accntProc, err := processProxy.NewAccountProcessor(bp, pubKeyConverter)
	if err != nil {
		return nil, err
	}

	faucetValue, _ := big.NewInt(0).SetString("10000000000000000000", 10)
	faucetProc, err := processFactory.CreateFaucetProcessor(bp, shardCoord, faucetValue, pubKeyConverter, args.PathToPemFile)
	if err != nil {
		return nil, err
	}

	txProc, err := processFactory.CreateTransactionProcessor(
		bp,
		pubKeyConverter,
		args.NodeHandler.GetCoreComponents().Hasher(),
		args.NodeHandler.GetCoreComponents().InternalMarshalizer(),
		args.Config.GeneralSettings.AllowEntireTxPoolFetch,
	)
	if err != nil {
		return nil, err
	}
	scQueryProc, err := processProxy.NewSCQueryProcessor(bp, pubKeyConverter)
	if err != nil {
		return nil, err
	}

	htbCacher := cache.NewHeartbeatMemoryCacher()
	cacheValidity := time.Duration(args.Config.GeneralSettings.HeartbeatCacheValidityDurationSec) * time.Second

	nodeGroupProc, err := processProxy.NewNodeGroupProcessor(bp, htbCacher, cacheValidity)
	if err != nil {
		return nil, err
	}

	valStatsCacher := cache.NewValidatorsStatsMemoryCacher()
	cacheValidity = time.Duration(args.Config.GeneralSettings.ValStatsCacheValidityDurationSec) * time.Second

	valStatsProc, err := processProxy.NewValidatorStatisticsProcessor(bp, valStatsCacher, cacheValidity)
	if err != nil {
		return nil, err
	}

	economicMetricsCacher := cache.NewGenericApiResponseMemoryCacher()
	cacheValidity = time.Duration(args.Config.GeneralSettings.EconomicsMetricsCacheValidityDurationSec) * time.Second

	nodeStatusProc, err := processProxy.NewNodeStatusProcessor(bp, economicMetricsCacher, cacheValidity)
	if err != nil {
		return nil, err
	}

	proxyInstance.closableComponents.Add(nodeGroupProc, valStatsProc, nodeStatusProc, bp)

	valStatsProc.StartCacheUpdate()
	nodeStatusProc.StartCacheUpdate()

	blockCacher, err := timecache.NewTimeCacher(timecache.ArgTimeCacher{
		DefaultSpan: time.Second,
		CacheExpiry: time.Duration(args.Config.GeneralSettings.BlockCacheDurationSec) * time.Second,
	})
	if err != nil {
		return nil, err
	}

	blockProc, err := processProxy.NewBlockProcessor(bp, blockCacher)
	if err != nil {
		return nil, err
	}

	blocksPrc, err := processProxy.NewBlocksProcessor(bp)
	if err != nil {
		return nil, err
	}

	proofProc, err := processProxy.NewProofProcessor(bp, pubKeyConverter)
	if err != nil {
		return nil, err
	}

	esdtSuppliesProc, err := processProxy.NewESDTSupplyProcessor(bp, scQueryProc)
	if err != nil {
		return nil, err
	}

	statusProc, err := processProxy.NewStatusProcessor(bp, statusMetricsProvider)
	if err != nil {
		return nil, err
	}

	aboutInfoProc, err := processProxy.NewAboutProcessor(bp, common.UnVersionedAppString, common.UndefinedCommitString)
	if err != nil {
		return nil, err
	}

	facadeArgs := versionsFactory.FacadeArgs{
		ActionsProcessor:             bp,
		AccountProcessor:             accntProc,
		FaucetProcessor:              faucetProc,
		BlockProcessor:               blockProc,
		BlocksProcessor:              blocksPrc,
		NodeGroupProcessor:           nodeGroupProc,
		NodeStatusProcessor:          nodeStatusProc,
		ScQueryProcessor:             scQueryProc,
		TransactionProcessor:         txProc,
		ValidatorStatisticsProcessor: valStatsProc,
		ProofProcessor:               proofProc,
		PubKeyConverter:              pubKeyConverter,
		ESDTSuppliesProcessor:        esdtSuppliesProc,
		StatusProcessor:              statusProc,
		AboutInfoProcessor:           aboutInfoProc,
	}

	apiConfigPath := path.Join(args.PathToConfig, "apiConfig")
	apiConfigParser, err := versionsFactory.NewApiConfigParser(apiConfigPath)
	if err != nil {
		return nil, err
	}

	versionsRegistry, err := versionsFactory.CreateVersionsRegistry(facadeArgs, apiConfigParser)
	if err != nil {
		return nil, err
	}
	port := args.Config.GeneralSettings.ServerPort

	proxyInstance.httpServer, err = api.CreateServer(
		versionsRegistry,
		port,
		args.Config.ApiLogging,
		config.CredentialsConfig{},
		statusMetricsProvider,
		args.Config.GeneralSettings.RateLimitWindowDurationSeconds,
		false,
		false,
	)
	if err != nil {
		return nil, err
	}

	return &ArgsOutputProxy{
		ProxyHandler:            proxyInstance,
		ProxyTransactionHandler: txProc,
	}, nil
}

// Start will start the proxy
func (p *proxy) Start() {
	go func() {
		err := p.httpServer.ListenAndServe()
		if err != nil {
			log.Debug("cannot ListenAndServe()", "err", err)
		}
	}()
}

// GetHttpServer will return the http server
func (p *proxy) GetHttpServer() *http.Server {
	return p.httpServer
}

// Close will close the proxy
func (p *proxy) Close() {
	p.closableComponents.Close()

	shutdownContext, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	_ = p.httpServer.Shutdown(shutdownContext)
	_ = p.httpServer.Close()
}
