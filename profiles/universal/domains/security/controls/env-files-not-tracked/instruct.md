# Why no .env files in working tree

`.gitignore` prevents accidental staging, but a forced `git add -f .env`
bypasses it. The deeper check: don't have a `.env` in the working tree
unless you actively need it.

## What to do

If you have a `.env`:
- Confirm it's not tracked: `git ls-files | grep .env` should return nothing
- Rename to `.env.example` if it's a template (no real secrets)
- Move to a tool-managed secrets store (1Password CLI, doppler, etc.) for
  real secrets

## Override

Active local dev with `.env` present is fine — declare an override with the
reason "active local-dev .env, gitignored, not for distribution."
