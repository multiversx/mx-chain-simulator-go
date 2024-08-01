import os
import re
import subprocess
import sys

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
        go_mod_path = './go.mod'

        print(f"go.mod path: {go_mod_path}")

        # Get the commit hash from the command-line argument
        if len(sys.argv) != 2:
            print("Usage: update_go_mod.py <commit_hash>")
            sys.exit(1)

        latest_commit_hash = sys.argv[1]
        print(f"Latest commit hash received: {latest_commit_hash}")

        # Update the go.mod file with the provided commit hash
        update_go_mod_file(go_mod_path, latest_commit_hash)

        print("Python Script executed successfully.")
    except Exception as e:
        print(f"Script execution failed: {str(e)}")
        sys.exit(1)
