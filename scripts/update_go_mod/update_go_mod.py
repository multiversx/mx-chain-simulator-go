import os
import re
import subprocess
import sys

def get_current_branch(repo_path):
    """
    Get the current branch name of the Git repository.
    """
    try:
        os.chdir(repo_path)
        result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(f"Failed to get the current branch name: {result.stderr.decode('utf-8')}")
            sys.exit(1)
        return result.stdout.decode('utf-8').strip()
    except Exception as e:
        print(f"Failed to determine the current branch: {str(e)}")
        sys.exit(1)

def get_latest_commit_hash(repo_path, branch_name):
    """
    Get the latest commit hash from the specified branch.
    """
    try:
        os.chdir(repo_path)
        # Fetch the latest changes to ensure you have the latest commits
        subprocess.run(['git', 'fetch'], check=True)
        # Checkout the branch explicitly to get the latest commit from that branch
        subprocess.run(['git', 'checkout', branch_name], check=True)
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(f"Failed to get the latest commit hash: {result.stderr.decode('utf-8')}")
            sys.exit(1)
        return result.stdout.decode('utf-8').strip()
    except Exception as e:
        print(f"Failed to obtain the latest commit hash: {str(e)}")
        sys.exit(1)

def update_go_mod_file(go_mod_path, new_hash):
    """
    Update the go.mod file with the new commit hash.
    """
    try:
        with open(go_mod_path, 'r') as file:
            content = file.read()

        # Use a regular expression to replace the version with the commit hash
        updated_content = re.sub(r'github\.com/multiversx/mx-chain-go\s+v[^\s]+', f'github.com/multiversx/mx-chain-go {new_hash}', content)

        with open(go_mod_path, 'w') as file:
            file.write(updated_content)

        print(f"Successfully updated go.mod with the latest commit hash: {new_hash}")
    except Exception as e:
        print(f"Failed to update go.mod file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        # Assuming the script is run from the root of mx-chain-simulator-go
        repo_path = '../mx-chain-go'
        go_mod_path = './go.mod'

        print(f"Repository path: {repo_path}")
        print(f"go.mod path: {go_mod_path}")

        # Get the current branch name
        current_branch = get_current_branch(repo_path)
        print(f"Current branch: {current_branch}")

        # Get the latest commit hash from the current branch
        latest_commit_hash = get_latest_commit_hash(repo_path, current_branch)
        update_go_mod_file(go_mod_path, latest_commit_hash)

        # Output the commit hash for GitHub Actions
        print(f"::set-output name=commit_hash::{latest_commit_hash}")
        print("Python Script executed successfully.")
    except Exception as e:
        print(f"Script execution failed: {str(e)}")
        sys.exit(1)
