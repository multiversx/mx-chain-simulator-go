package configs

import (
	"os"
	"path"
	"runtime/debug"
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
}

// NewConfigsFetcher will create a new instance of fetcher
func NewConfigsFetcher(mxChainNodeRepo, mxChainProxy string, git GitHandler, isSovereign bool) (*fetcher, error) {
	return &fetcher{
		mxChainNodeRepo: mxChainNodeRepo,
		mxChainProxy:    mxChainProxy,
		gitFetcher:      git,
		isSovereign:     isSovereign,
	}, nil
}

// FetchProxyConfigs will try to fetch the proxy configs
func (f *fetcher) FetchProxyConfigs(info *debug.BuildInfo, pathWhereToPutConfigs string) error {
	exists, err := folderExists(pathWhereToPutConfigs)
	if err != nil {
		return err
	}
	if exists {
		return nil
	}

	mxProxyTag := extractTag(info, f.mxChainProxy)
	log.Info("fetching proxy configs...", "repo", f.mxChainProxy, "version", mxProxyTag)

	return f.fetchConfigFolder(f.mxChainProxy, mxProxyTag, pathWhereToPutConfigs, appProxy)
}

// FetchNodeConfigs will try to fetch the node configs
func (f *fetcher) FetchNodeConfigs(info *debug.BuildInfo, pathWhereToPutConfigs string) error {
	exists, err := folderExists(pathWhereToPutConfigs)
	if err != nil {
		return err
	}
	if exists {
		return nil
	}

	mxNodeTag := extractTag(info, f.mxChainNodeRepo)
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

func extractTag(info *debug.BuildInfo, repo string) string {
	for _, dep := range info.Deps {
		actualPath := dep.Path
		if dep.Replace != nil {
			actualPath = dep.Replace.Path
		}
		if strings.Contains(repo, actualPath) {
			return extractVersionOrCommit(dep.Version)
		}
	}

	return ""
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
