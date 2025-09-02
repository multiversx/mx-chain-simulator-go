import os
import re
import sys
import subprocess

def update_go_mod_file(go_mod_path, new_hash, new_core_go_hash):
    """
    Update the go.mod file with the new commit hash.
    """
    try:
        with open(go_mod_path, 'r') as file:
            content = file.read()
        # Print the original content for debugging
        print("Original go.mod content:")
        print(content)
        updated_content = re.sub(r'(github\.com/multiversx/mx-chain-sovereign-go\s+)[^\s]+',f'github.com/multiversx/mx-chain-sovereign-go {new_hash}', content)
        updated_content = re.sub(r'(github\.com/multiversx/mx-chain-core-sovereign-go\s+)[^\s]+',f'github.com/multiversx/mx-chain-core-sovereign-go {new_core_go_hash}', updated_content)

        # Print updated content for verification
        print("Updated go.mod content:")
        print(updated_content)

        # Write the updated content back to the file
        with open(go_mod_path, 'w') as file:
            file.write(updated_content)

        print(f"Successfully updated go.mod with the latest commit hash: {new_hash}")
    except Exception as e:
        print(f"Failed to update go.mod file: {str(e)}")
        sys.exit(1)

def run_go_mod_tidy():
    """
    Run `go mod tidy` to ensure the go.mod file is tidy.
    """
    try:
        print("Running go mod tidy...")
        subprocess.run(['go', 'mod', 'tidy'], check=True)
        print("Successfully ran go mod tidy.")

    except subprocess.CalledProcessError as e:
        print(f"Failed to run go mod tidy: {e.stderr}")
        sys.exit(1)

def main():
    # Assuming the script is run from the root of mx-chain-simulator-go
    go_mod_path = './go.mod'

    if len(sys.argv) != 3:
        print("Usage: update-go-mod.py <commit_hash>")
        sys.exit(1)

    latest_commit_hash = sys.argv[1]
    latest_core_go_hash = sys.argv[2]

    print(f"go.mod path: {go_mod_path}")
    print(f"Latest commit hash received: {latest_commit_hash}")
    print(f"Latest core go commit hash received: {latest_core_go_hash}")

    update_go_mod_file(go_mod_path, latest_commit_hash, latest_core_go_hash)

    # Run go mod tidy after updating go.mod
    run_go_mod_tidy()

    print("Python Script executed successfully.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Main() Script execution failed: {str(e)}")
        sys.exit(1)
