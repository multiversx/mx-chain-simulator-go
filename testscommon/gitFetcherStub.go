package testscommon

type GitFetcherStub struct {
	CloneCalled func(r, d string) error
}

func (gf *GitFetcherStub) Clone(repo, dir string) error {
	if gf.CloneCalled != nil {
		return gf.CloneCalled(repo, dir)
	}

	return nil
}

func (gf *GitFetcherStub) Checkout(_, _ string) error {
	return nil
}
