import os
import re
import subprocess
import sys

def get_latest_commit_hash(repo_path):
    os.chdir(repo_path)
    result = subprocess.run(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Failed to get the latest commit hash: {result.stderr.decode('utf-8')}")
        sys.exit(1)
    return result.stdout.decode('utf-8').strip()

def update_go_mod_file(go_mod_path, new_hash):
    try:
        with open(go_mod_path, 'r') as file:
            content = file.read()

        updated_content = re.sub(r'github\.com/multiversx/mx-chain-go\s+v[^\s]+', f'github.com/multiversx/mx-chain-go {new_hash}', content)

        with open(go_mod_path, 'w') as file:
            file.write(updated_content)

        print(f"Successfully updated go.mod with latest commit hash: {new_hash}")
    except Exception as e:
        print(f"Failed to update go.mod file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        repo_path = 'mx-chain-go'
        go_mod_path = 'mx-chain-simulator-go/go.mod'

        latest_commit_hash = get_latest_commit_hash(repo_path)
        update_go_mod_file(go_mod_path, latest_commit_hash)

        print(f"::set-output name=commit_hash::{latest_commit_hash}")
        print("Script executed successfully.")
    except Exception as e:
        print(f"Script execution failed: {str(e)}")
        sys.exit(1)
