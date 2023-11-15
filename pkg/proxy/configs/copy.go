package configs

import (
	"io"
	"os"
	"path/filepath"
)

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
		defer func() {
			_ = in.Close()
		}()

		out, err := os.Create(filepath.Join(dst, relPath))
		if err != nil {
			return err
		}

		_, err = io.Copy(out, in)
		if err != nil {
			_ = out.Close()
			return err
		}

		return out.Close()
	})
}
