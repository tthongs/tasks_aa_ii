#!/bin/bash
# Helper script to stage, commit, and auto-push logged issue documentation.

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$REPO_ROOT" ]; then
    echo "Error: Not a git repository."
    exit 1
fi

cd "$REPO_ROOT" || exit 1

ISSUE_FILE="$1"
COMMIT_MSG="$2"

# Stage modified/untracked files in issues/ directory or specified issue file
if [ -n "$ISSUE_FILE" ] && [ -f "$ISSUE_FILE" ]; then
    git add "$ISSUE_FILE"
fi

git add issues/ .githooks/

if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="docs(issues): update issue log and auto-push"
fi

echo "Staging files and committing..."
git commit -m "$COMMIT_MSG"

# Note: The git post-commit hook automatically executes git push, but we verify here.
if [ $? -eq 0 ]; then
    echo "Commit succeeded. Post-commit hook handles remote auto-push."
else
    echo "Commit failed or no changes to commit."
fi
