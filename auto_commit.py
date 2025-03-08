#!/usr/bin/env python3
import subprocess

COMMIT_MESSAGE_PROMPT = """
Analyze the following git diff and generate a commit message using Conventional Commit format.
Be brief and concise, dont mention filename ,use bullets to separate changes"""
CONVENTIONAL_COMMIT_PROMPT = """
Analyze the following git diff and generate a commit message using Conventional Commit format.
Be brief and concise, dont mention filename ,use bullets to separate changes
##Conventional Commit format
```<type>[optional scope]: <description>

[optional body]

[optional footer(s)]```

The commit type can be:
- feat: Commits, which adds a new feature
- fix: Commits, that fixes a bug
- refactor: Commits, that rewrite/restructure your code, however, do not change any behavior
- perf: Commits are special refactor commits, that improve performance
- style: Commits, that do not affect the meaning (white space, formatting, missing semi-colons, etc)
- test: Commits, that add missing tests or correct existing tests
- docs: Commits, that affect documentation only
- build: Commits, that affect build components like build tool, ci pipeline, dependencies, project version, ...
- ops: Commits, that affect operational components like infrastructure, deployment, backup, recovery...
- chore: Miscellaneous commits e.g. modifying .gitignore

A scope MUST consist of a noun describing a section of the codebase surrounded by parenthesis. ```eg feat(profile): add button for update call```
Follow these rules for creating the great commit message
- Limit the subject line to 50 characters
- Capitalize the subject/description line
- Do not end the subject line with a period
- Separate the subject from the body with a blank line
- Use the imperative mood in the subject line
- Wrap the body at 72 characters
- Use the body to explain what and why
"""


def get_git_diff():
    try:
        subprocess.run(['git', 'add', '.'],
                       capture_output=True,
                       text=True,
                       check=True)

        result = subprocess.run(['git', 'diff', '--minimal'],
                                capture_output=True,
                                text=True,
                                check=True)
        result2 = subprocess.run(['git', 'diff', '--staged', '--minimal'],
                                 capture_output=True,
                                 text=True,
                                 check=True)
        return f"{result.stdout}\n{result2.stdout}"
    except subprocess.CalledProcessError as e:
        print(f"Error getting git diff: {str(e)}")
        return None


def get_commit_message(system_prompt, git_diff_output):
    try:
        # First, read the file
        prompt = f'{system_prompt}"""{git_diff_output}"""'[:8000]
        # Then run gh models
        result = subprocess.run(['gh', 'models', 'run', 'gpt-4o'],
                                input=prompt,
                                capture_output=True,
                                text=True,
                                check=True)

        return result.stdout.replace("```", "").strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running gh models: {str(e)}")
        print(f"stderr: {e.stderr}")
        return None
    except FileNotFoundError as e:
        print(f"Error reading file: {str(e)}")
        return None


def get_user_confirmation_for_commit(commit_message):
    print(f"\nProposed commit message:\n{'-' * 50}\n{commit_message}\n{'-' * 50}")
    while True:
        response = input("\nDo you want to proceed with this commit? (y/n): ").lower().strip()
        if response in ['y', 'n']:
            return response == 'y'
        print("Please enter 'y' for yes or 'n' for no.")

def get_user_confirmation_for_push():
    while True:
        response = input("\nDo you want to push commit(s) to remote? (y/n): ").lower().strip()
        if response in ['y', 'n']:
            return response == 'y'
        print("Please enter 'y' for yes or 'n' for no.")

def main():
    git_diff_output = get_git_diff()
    if git_diff_output:

        try:
            # Your existing code to generate commit message
            commit_message = get_commit_message(system_prompt=COMMIT_MESSAGE_PROMPT, git_diff_output=git_diff_output)

            if not commit_message:
                print("Failed to generate commit message. Aborting.")
                print("-" * 80)
                print(git_diff_output)
                return
            # Ask for user confirmation
            if get_user_confirmation_for_commit(commit_message):
                # Proceed with git commit
                subprocess.run(['git', 'commit', '-m', commit_message], check=True)
                print("Changes committed successfully!")
                if get_user_confirmation_for_push():
                    subprocess.run(['git', 'push'], check=True)
                    print("Changes pushed successfully!")
                else:
                    print("Git push cancelled by user.")
            else:
                print("Commit cancelled by user.")

        except subprocess.CalledProcessError as e:
            print(f"Error during git operations: {e}")
            print(f"Error output: {e.stderr}")


    else:
        print("No git diff found.")


if __name__ == '__main__':
    main()
