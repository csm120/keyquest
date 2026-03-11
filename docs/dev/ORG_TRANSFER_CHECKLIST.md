# Organization Transfer Checklist

This checklist documents the move of `KeyQuest` from `csm120` to `WebFriendlyHelp`
and can be reused for similar future transfers.

## What Cannot Be Automated Here

- GitHub organization creation must be done in GitHub's web UI.
- This session does not have the `admin:org` scope needed for org administration.

## Recommended Setup

- Create the `WebFriendlyHelp` organization.
- Keep `csm120` as an org owner.
- Transfer `KeyQuest` only after the org exists and you have owner access.

## Before Transfer

1. Create the organization in GitHub.
2. Confirm the final target is `WebFriendlyHelp/KeyQuest`.
3. Review current repo settings:
   - Issues
   - Discussions
   - Actions
   - Pages
   - Branch protection
   - Secrets and environments
4. Preview link updates:

```powershell
py tools/dev/update_repo_links.py --new-owner WebFriendlyHelp
```

## Transfer

1. Open the repository settings for the current source repo.
2. Use GitHub's transfer flow to move it to the target organization, such as `WebFriendlyHelp`.
3. Confirm the repo remains public after transfer.

## After Transfer

1. Apply owner-link updates:

```powershell
py tools/dev/update_repo_links.py --new-owner WebFriendlyHelp --apply
```

2. Review the changed files and commit them.
3. Verify:
   - `README` badges load
   - release download links work
   - GitHub Pages is configured correctly
   - in-app help and issue links open the new repo
   - Actions and Pages still publish successfully
4. Post a short note in Discussions or the README if you want contributors to know the repo moved.
