# Why .env must be gitignored

Coding agents create `.env` files routinely — for local dev, for testing
with real API keys, for spinning up services. If `.env` is not in
`.gitignore`, the next `git add .` or `git commit -a` commits the secret.

By the time someone notices, the secret is in history. Rotating secrets
out of history is painful: BFG-repo-cleaner, force-push, every collaborator
re-clones. Prevention costs two lines in `.gitignore`.

## What to add

```
.env
.env.*
```

Some projects use a tracked `.env.example` template. Add it as an explicit
exception:
```
.env
.env.*
!.env.example
```

## When to override

If your project genuinely has no secrets and no .env workflow (rare, e.g.
a static site), you may override. Document the reason in `.agent-weiss.yaml`.

## Rego unit-test check

`policy_test.rego` exercises the deny rules in isolation. Run with
`conftest verify --policy policy.rego` from this directory.
