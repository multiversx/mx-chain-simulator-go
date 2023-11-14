package configs

import (
	"fmt"
	"io"
	"os"
	"os/exec"
	"path"
	"path/filepath"
	"runtime/debug"
	"strings"

	logger "github.com/multiversx/mx-chain-logger-go"
)

var log = logger.GetOrCreate("configs")

const (
	mxNodeRepo  = "https://github.com/multiversx/mx-chain-go"
	mxProxyRepo = "https://github.com/multiversx/mx-chain-proxy-go"

	appNode  = "node"
	appProxy = "proxy"
)

type fetcher struct {
}

func NewConfigsFetcher() (*fetcher, error) {
	return &fetcher{}, nil
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

	mxProxyTag := extractTag(info, mxProxyRepo)
	log.Info("fetching proxy configs...", "repo", mxProxyRepo, "version", mxProxyTag)

	return f.fetchConfigFolder(mxProxyRepo, mxProxyTag, pathWhereToPutConfigs, appProxy)
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

	mxNodeTag := extractTag(info, mxNodeRepo)
	log.Info("fetching node configs...", "repo", mxNodeRepo, "version", mxNodeTag)

	return f.fetchConfigFolder(mxNodeRepo, mxNodeTag, pathWhereToPutConfigs, appNode)
}

func (f *fetcher) fetchConfigFolder(repo string, version string, pathWhereToSaveConfig string, app string) error {
	pathToRepo := path.Join(os.TempDir(), "repo")
	err := cloneRepository(repo, pathToRepo)
	if err != nil {
		return err
	}

	err = checkoutCommit(pathToRepo, version)
	if err != nil {
		return err
	}

	pathToRepoConfigs := path.Join(pathToRepo, "cmd", app, "config")
	err = copyFolderWithAllFiles(pathToRepoConfigs, pathWhereToSaveConfig)
	if err != nil {
		return err
	}

	return os.RemoveAll(pathToRepo)
}

func extractTag(info *debug.BuildInfo, repo string) string {
	for _, dep := range info.Deps {
		if strings.Contains(repo, dep.Path) {
			return extractVersionOrCommit(dep.Version)
		}
	}

	return ""
}

func extractVersionOrCommit(versionStr string) string {
	if strings.Contains(versionStr, "-") {
		parts := strings.Split(versionStr, "-")
		return parts[len(parts)-1]
	}
	return versionStr
}

func cloneRepository(repoURL, destDir string) error {
	cmd := exec.Command("git", "clone", repoURL, destDir)
	res, err := cmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("%s-%s", string(res), err.Error())
	}

	return nil
}

func checkoutCommit(repoDir, commitHash string) error {
	cmd := exec.Command("git", "checkout", commitHash)
	cmd.Dir = repoDir

	res, err := cmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("%s-%s", string(res), err.Error())
	}

	return nil
}

func copyFolderWithAllFiles(src, dst string) error {
	return filepath.Walk(src, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		relPath, err := filepath.Rel(src, path)
		if err != nil {
			return err
		}

		if info.IsDir() {
			return os.MkdirAll(filepath.Join(dst, relPath), info.Mode())
		}

		in, err := os.Open(path)
		if err != nil {
			return err
		}
		defer in.Close()

		out, err := os.Create(filepath.Join(dst, relPath))
		if err != nil {
			return err
		}
		defer out.Close()

		_, err = io.Copy(out, in)
		if err != nil {
			return err
		}

		return out.Close()
	})
}

func folderExists(folderPath string) (bool, error) {
	_, err := os.Stat(folderPath)
	if os.IsNotExist(err) {
		return false, nil
	} else if err != nil {
		return false, err
	}

	return true, nil
}
