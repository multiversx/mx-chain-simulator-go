package configs

// GitHandler defines what a git handler should be able to do
type GitHandler interface {
	Clone(repoURL, destDir string) error
	Checkout(repoDir string, commitHashOrBranch string) error
}
