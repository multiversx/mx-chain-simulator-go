package configs

import (
	"fmt"
	"os"
	"path"
	"strings"

	logger "github.com/multiversx/mx-chain-logger-go"
)

var log = logger.GetOrCreate("configs")

const (
	appNode  = "node"
	appProxy = "proxy"
)

type fetcher struct {
	gitFetcher      GitHandler
	mxChainNodeRepo string
	mxChainProxy    string
	isSovereign     bool
	goModUrl        string
}

// NewConfigsFetcher will create a new instance of fetcher
func NewConfigsFetcher(mxChainNodeRepo, mxChainProxy string, git GitHandler, isSovereign bool, goModUrl string) (*fetcher, error) {
	return &fetcher{
		mxChainNodeRepo: mxChainNodeRepo,
		mxChainProxy:    mxChainProxy,
		gitFetcher:      git,
		isSovereign:     isSovereign,
		goModUrl:        goModUrl,
	}, nil
}

// FetchProxyConfigs will try to fetch the proxy configs
func (f *fetcher) FetchProxyConfigs(pathWhereToPutConfigs string) error {
	exists, err := folderExists(pathWhereToPutConfigs)
	if err != nil {
		return err
	}
	if exists {
		return nil
	}

	mxProxyTag, err := f.extractTag(f.mxChainProxy)
	if err != nil {
		return err
	}
	log.Info("fetching proxy configs...", "repo", f.mxChainProxy, "version", mxProxyTag)

	return f.fetchConfigFolder(f.mxChainProxy, mxProxyTag, pathWhereToPutConfigs, appProxy)
}

// FetchNodeConfigs will try to fetch the node configs
func (f *fetcher) FetchNodeConfigs(pathWhereToPutConfigs string) error {
	exists, err := folderExists(pathWhereToPutConfigs)
	if err != nil {
		return err
	}
	if exists {
		return nil
	}

	mxNodeTag, err := f.extractTag(f.mxChainNodeRepo)
	if err != nil {
		return err
	}
	log.Info("fetching node configs...", "repo", f.mxChainNodeRepo, "version", mxNodeTag)

	return f.fetchConfigFolder(f.mxChainNodeRepo, mxNodeTag, pathWhereToPutConfigs, appNode)
}

func (f *fetcher) fetchConfigFolder(repo string, version string, pathWhereToSaveConfig string, app string) error {
	pathToRepo := path.Join(os.TempDir(), "repo")
	err := f.gitFetcher.Clone(repo, pathToRepo)
	if err != nil {
		return err
	}

	err = f.gitFetcher.Checkout(pathToRepo, version)
	if err != nil {
		return err
	}

	pathToRepoConfigs := path.Join(pathToRepo, "cmd", app, "config")
	err = copyFolderWithAllFiles(pathToRepoConfigs, pathWhereToSaveConfig)
	if err != nil {
		return err
	}

	// TODO MX-16540 refactor to use RunType components
	if f.isSovereign && app == appNode {
		pathToRepoConfigs = path.Join(pathToRepo, "cmd", "sovereignnode", "config")
		err = copyFolderWithAllFiles(pathToRepoConfigs, strings.Replace(pathWhereToSaveConfig, "/node", "/sovereignnode", 1))
		if err != nil {
			return err
		}
	}

	return os.RemoveAll(pathToRepo)
}

// extract commit hash from go.mod file
func (f *fetcher) extractTag(repoURL string) (string, error) {
	modulePath := strings.TrimPrefix(repoURL, "https://")

	data, err := os.ReadFile(f.goModUrl)
	if err != nil {
		return "", err
	}

	lines := strings.Split(string(data), "\n")
	for _, line := range lines {
		if strings.Contains(line, modulePath) {
			parts := strings.Fields(line)
			return extractVersionOrCommit(parts[len(parts)-1]), nil
		}
	}

	return "", fmt.Errorf("module %s not found in go.mod", modulePath)
}

func extractVersionOrCommit(versionStr string) string {
	if !strings.Contains(versionStr, "-sov") {
		parts := strings.Split(versionStr, "-")
		return parts[len(parts)-1]
	}
	return versionStr
}

func folderExists(folderPath string) (bool, error) {
	_, err := os.Stat(folderPath)
	if os.IsNotExist(err) {
		return false, nil
	}

	return true, nil
}
