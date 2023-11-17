package testscommon

// GitFetcherStub -
type GitFetcherStub struct {
	CloneCalled func(r, d string) error
}

// Clone -
func (gf *GitFetcherStub) Clone(repo, dir string) error {
	if gf.CloneCalled != nil {
		return gf.CloneCalled(repo, dir)
	}

	return nil
}

// Checkout -
func (gf *GitFetcherStub) Checkout(_, _ string) error {
	return nil
}
