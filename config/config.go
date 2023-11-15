package config

// Config will hold the whole config file's data
type Config struct {
	Config struct {
		ServerPort int `toml:"server-port"`
		Logs       struct {
			LogFileLifeSpanInMB  int    `toml:"log-file-life-span-in-mb"`
			LogFileLifeSpanInSec int    `toml:"log-file-life-span-in-sec"`
			LogFilePrefix        string `toml:"log-file-prefix"`
			LogsPath             string `toml:"logs-path"`
		} `toml:"logs"`
	} `toml:"config"`
}
