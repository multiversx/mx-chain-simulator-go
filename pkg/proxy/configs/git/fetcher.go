package git

import (
	"fmt"
	"os"
	"os/exec"
)

type gitFetcher struct{}

// NewGitFetcher will create a new instance of gitFetcher
func NewGitFetcher() *gitFetcher {
	return &gitFetcher{}
}

// Clone will clone the provided git repository in the provided destination dir
func (gf *gitFetcher) Clone(repoURL, destDir string) error {
	cmd := exec.Command("git", "clone", repoURL, destDir)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Stdin = os.Stdin
	return cmd.Run()
}

// Checkout will checkout or commit hash from the provided repository directory
func (gf *gitFetcher) Checkout(repoDir string, commitHashOrBranch string) error {
	cmd := exec.Command("git", "checkout", commitHashOrBranch)
	cmd.Dir = repoDir

	res, err := cmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("%s-%s", string(res), err.Error())
	}

	return nil
}
