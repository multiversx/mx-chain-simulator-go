package configs

import (
	"os/exec"
	"path"

	"github.com/multiversx/mx-chain-core-go/core"
	"github.com/multiversx/mx-chain-proxy-go/config"
	"github.com/multiversx/mx-chain-proxy-go/data"
)

const (
	httpPrefix = "http://"
)

// ArgsProxyConfigs holds the arguments needed to create the proxy configs
type ArgsProxyConfigs struct {
	TemDir            string
	PathToProxyConfig string
	ServerPort        int
	RestApiInterfaces map[uint32]string
}

// ArgsOutputConfig holds the output arguments for proxy configs
type ArgsOutputConfig struct {
	Config           *config.Config
	PathToTempConfig string
}

// CreateProxyConfigs will create the proxy configs
func CreateProxyConfigs(args ArgsProxyConfigs) (*ArgsOutputConfig, error) {
	newConfigsPath := path.Join(args.TemDir, "proxyConfig")

	cmd := exec.Command("cp", "-r", args.PathToProxyConfig, newConfigsPath)
	err := cmd.Run()
	if err != nil {
		return nil, err
	}

	cfg := &config.Config{}
	tomlFilePath := path.Join(newConfigsPath, "config.toml")
	err = core.LoadTomlFile(cfg, tomlFilePath)
	if err != nil {
		return nil, err
	}

	cfg.GeneralSettings.ServerPort = args.ServerPort
	cfg.Observers = make([]*data.NodeData, 0, len(args.RestApiInterfaces))
	for shardID, nodeAPIInterface := range args.RestApiInterfaces {
		cfg.Observers = append(cfg.Observers, &data.NodeData{
			ShardId:  shardID,
			Address:  httpPrefix + nodeAPIInterface,
			IsSynced: true,
		})
	}

	return &ArgsOutputConfig{
		Config:           cfg,
		PathToTempConfig: newConfigsPath,
	}, nil
}
