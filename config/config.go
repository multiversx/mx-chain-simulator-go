package config

// Config will hold the whole config file's data
type Config struct {
	Config struct {
		Simulator struct {
			ServerPort        int    `toml:"server-port"`
			NumOfShards       int    `toml:"num-of-shards"`
			RoundsPerEpoch    int    `toml:"rounds-per-epoch"`
			RoundDurationInMs int    `toml:"round-duration-in-milliseconds"`
			InitialRound      int64  `toml:"initial-round"`
			InitialNonce      uint64 `toml:"initial-nonce"`
			InitialEpoch      uint32 `toml:"initial-epoch"`
			MxChainRepo       string `toml:"mx-chain-go-repo"`
			MxProxyRepo       string `toml:"mx-chain-proxy-go-repo"`
		} `toml:"simulator"`
		Logs struct {
			LogFileLifeSpanInMB  int    `toml:"log-file-life-span-in-mb"`
			LogFileLifeSpanInSec int    `toml:"log-file-life-span-in-sec"`
			LogFilePrefix        string `toml:"log-file-prefix"`
			LogsPath             string `toml:"logs-path"`
		} `toml:"logs"`
		BlocksGenerator BlocksGeneratorConfig `toml:"blocks-generator"`
	} `toml:"config"`
}

// BlocksGeneratorConfig defined the configuration for the blocks generator
type BlocksGeneratorConfig struct {
	AutoGenerateBlocks bool   `toml:"auto-generate-blocks"`
	BlockTimeInMs      uint64 `toml:"block-time-in-milliseconds"`
}
