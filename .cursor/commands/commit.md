## Commit Requirements

When committing changes, you must follow these mandatory rules:

1. **Commit all uncommitted files**: All uncommitted files must be committed in a single commit.

2. **Write a descriptive message**: Write a commit message that clearly describes all the changes made.

3. **Include codex identifier**: Every commit message must include a codex identifier per project standard. Use the format `[CODEX-XXX]` where XXX is a unique identifier for the change set.

4. **Ensure changelog entries exist**: Before pushing, ensure that appropriate changelog entries exist documenting the changes. Note: This is enforced by a pre-push hook that will prevent pushing if changelog entries are missing.

5. **Use /push command for final push**: After committing, use the `/push` command for the final push after manual review. Do not auto-commit or auto-push. The `/push` command allows for review before pushing to the remote repository.

## Commit Message Template

```
[CODEX-XXX] Brief summary of changes

- Change 1: Description of first change
- Change 2: Description of second change
- Change 3: Description of third change
```

Example:
```
[CODEX-142] Expand commit guidance with codex identifier and changelog requirements

- Add mandatory codex identifier requirement to commit messages
- Require changelog entries before push (enforced by pre-push hook)
- Document use of /push command for final push after review
- Include commit message template with codex tag and bullet list format
```
