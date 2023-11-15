package configs

import (
	"encoding/hex"
	"encoding/pem"
	"os"
	"os/exec"
	"path"

	"github.com/multiversx/mx-chain-core-go/core"
	"github.com/multiversx/mx-chain-go/node/chainSimulator/dtos"
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
	InitialWallets    map[uint32]*dtos.WalletKey
	AddressConverter  core.PubkeyConverter
}

// ArgsOutputConfig holds the output arguments for proxy configs
type ArgsOutputConfig struct {
	Config           *config.Config
	PathToTempConfig string
	PathToPemFile    string
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

	pemFile := path.Join(newConfigsPath, "walletKey.pem")
	err = generatePemFromInitialAddress(pemFile, args.InitialWallets, args.AddressConverter)
	if err != nil {
		return nil, err
	}

	return &ArgsOutputConfig{
		Config:           cfg,
		PathToTempConfig: newConfigsPath,
		PathToPemFile:    pemFile,
	}, nil
}

func generatePemFromInitialAddress(fileName string, initialAddresses map[uint32]*dtos.WalletKey, addressConverter core.PubkeyConverter) error {
	file, errO := os.OpenFile(fileName, os.O_CREATE|os.O_WRONLY, core.FileModeReadWrite)
	if errO != nil {
		return errO
	}

	for _, wallet := range initialAddresses {
		addressBytes, err := addressConverter.Decode(wallet.Address)
		if err != nil {
			return err
		}

		skBytes := append([]byte(wallet.PrivateKeyHex), []byte(hex.EncodeToString(addressBytes))...)
		blk := pem.Block{
			Type:  "PRIVATE KEY for " + wallet.Address,
			Bytes: skBytes,
		}

		err = pem.Encode(file, &blk)
		if err != nil {
			return err
		}
	}

	return nil
}
