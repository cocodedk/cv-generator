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

  # Run tests using the existing test script
  # Output to stderr so it doesn't interfere with JSON output
  if [ -f "scripts/run-tests.sh" ]; then
    echo "Running tests to verify changes..." >&2
    bash scripts/run-tests.sh >&2 || true  # Don't fail the hook if tests fail
  fi

  # Return a followup message that will be automatically submitted
  # This asks the agent to update tests (if needed) and documentation
  # The agent can use /update-tests and /update-docs commands
  cat <<EOF
{
  "followup_message": "Please review the test results above. Use /update-tests to update any failing tests and /update-docs to ensure documentation in the docs/ directory is accurate and reflects the recent changes."
}
EOF
else
  # No followup message
  echo "{}"
fi

exit 0
