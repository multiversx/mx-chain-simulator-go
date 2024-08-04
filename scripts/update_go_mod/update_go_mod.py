import os
import re
import sys

def update_go_mod_file(go_mod_path, new_hash):
    """
    Update the go.mod file with the new commit hash.
    """
    try:
        with open(go_mod_path, 'r') as file:
            content = file.read()

        # Print the original content for debugging
        print("Original go.mod content:")
        print(content)

        # Simplified regex to only capture the version part
        updated_content = re.sub(r'(github\.com/multiversx/mx-chain-go\s+)(v[^\s]+)', r'github.com/multiversx/mx-chain-go ' + new_hash, content)

        with open(go_mod_path, 'w') as file:
            file.write(updated_content)

        print(f"Successfully updated go.mod with the latest commit hash: {new_hash}")
    except Exception as e:
        print(f"Failed to update go.mod file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        go_mod_path = os.path.join(script_dir, '../../go.mod')

        print(f"go.mod path: {go_mod_path}")

        if len(sys.argv) != 2:
            print("Usage: update_go_mod.py <commit_hash>")
            sys.exit(1)

        latest_commit_hash = sys.argv[1]
        print(f"Latest commit hash received: {latest_commit_hash}")

        update_go_mod_file(go_mod_path, latest_commit_hash)

        print("Python Script executed successfully.")
    except Exception as e:
        print(f"Script execution failed: {str(e)}")
        sys.exit(1)
