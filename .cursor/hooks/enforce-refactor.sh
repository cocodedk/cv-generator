#!/bin/bash

# Hook script that prompts the agent to follow the refactor command guidance
# This hook is called when the agent loop ends

# Read JSON input from stdin
input=$(cat)

# Parse the status and loop count
status=$(echo "$input" | jq -r '.status')
loop_count=$(echo "$input" | jq -r '.loop_count // 0')

# Only trigger if task completed successfully and we haven't looped too many times
if [ "$status" = "completed" ] && [ "$loop_count" -lt 2 ]; then
  cat <<EOF
{
  "followup_message": "Please apply the /refactor command and follow the guidance in .cursor/commands/refactor.md (split into smaller files, keep ~135–160 lines, run tests, and update docs)."
}
EOF
else
  echo "{}"
fi

exit 0
