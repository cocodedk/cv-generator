#!/bin/bash

# Hook script that automatically runs tests and prompts to update docs after task completion
# This hook is called when the agent loop ends

# Read JSON input from stdin
input=$(cat)

# Parse the status and workspace root
status=$(echo "$input" | jq -r '.status')
loop_count=$(echo "$input" | jq -r '.loop_count // 0')
workspace_root=$(echo "$input" | jq -r '.workspace_roots[0]')

# Only trigger if task completed successfully and we haven't looped too many times
if [ "$status" = "completed" ] && [ "$loop_count" -lt 2 ]; then
  # Change to workspace root
  cd "$workspace_root" || exit 1

  echo "Update tests hook: status=$status loop_count=$loop_count workspace_root=$workspace_root" >&2

  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Update tests hook: not a git repo, exiting" >&2
    echo "{}"
    exit 0
  fi

  if git diff --quiet && git diff --cached --quiet; then
    echo "Update tests hook: working tree clean, exiting" >&2
    echo "{}"
    exit 0
  fi

  # Run tests using the existing test script
  # Output to stderr so it doesn't interfere with JSON output
  test_status=0
  if [ -f "scripts/run-tests.sh" ]; then
    echo "Running tests to verify changes..." >&2
    bash scripts/run-tests.sh >&2
    test_status=$?
  else
    echo "Update tests hook: scripts/run-tests.sh not found, skipping tests" >&2
  fi

  if [ "$test_status" -eq 0 ]; then
    if ! git diff --quiet || ! git diff --cached --quiet; then
      git add -A
      files=$(git diff --cached --name-only)
      if [ -n "$files" ]; then
        {
          echo "chore: update files"
          echo ""
          echo "$files"
        } | git commit -F - >/dev/null 2>&1 || true
      fi
    fi

    echo "{}"
  else
    # Return a followup message that will be automatically submitted
    # This asks the agent to update tests (if needed) and documentation
    # The agent can use /update-tests and /update-docs commands
    cat <<EOF
{
  "followup_message": "Please review the test results above. Use /update-tests to update any failing tests and /update-docs to ensure documentation in the docs/ directory is accurate and reflects the recent changes."
}
EOF
  fi
else
  # No followup message
  echo "{}"
fi

exit 0
