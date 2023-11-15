package configs

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestCopyFolderWithAllFiles(t *testing.T) {
	src := t.TempDir()
	dst := t.TempDir()

	var err error
	files := []string{"file1.txt", "file2.txt", "dir/file3.txt"}
	for _, file := range files {
		path := filepath.Join(src, file)
		err = os.MkdirAll(filepath.Dir(path), 0755)
		require.Nil(t, err)

		err = os.WriteFile(path, []byte("Hello, World!"), 0644)
		require.Nil(t, err)
	}

	err = copyFolderWithAllFiles(src, dst)
	require.Nil(t, err)

	for _, file := range files {
		_, err = os.Stat(filepath.Join(dst, file))
		if os.IsNotExist(err) {
			t.Errorf("file %s was not copied", file)
		} else if err != nil {
			t.Error(err)
		}
	}
}

func TestCopyFolderWithAllFilesNonExistentSrc(t *testing.T) {
	dst := t.TempDir()

	err := copyFolderWithAllFiles("/path/to/non/existent/directory", dst)
	require.NotNil(t, err)
}
