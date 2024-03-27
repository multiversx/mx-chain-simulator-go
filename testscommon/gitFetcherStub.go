package testscommon

// GitFetcherStub -
type GitFetcherStub struct {
	CloneCalled    func(r, d string) error
	CheckoutCalled func(repoDir string, commitHashOrBranch string) error
}

// Clone -
func (gf *GitFetcherStub) Clone(repo, dir string) error {
	if gf.CloneCalled != nil {
		return gf.CloneCalled(repo, dir)
	}

	return nil
}

// Checkout -
func (gf *GitFetcherStub) Checkout(repoDir string, commitHashOrBranch string) error {
	if gf.CheckoutCalled != nil {
		return gf.CheckoutCalled(repoDir, commitHashOrBranch)
	}

	return nil
}
