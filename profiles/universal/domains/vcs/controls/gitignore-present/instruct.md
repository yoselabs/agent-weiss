# Why .gitignore

A `.gitignore` is the single most important file for keeping a repository
clean. Without it: build artifacts pollute commits, IDE/.DS_Store noise
appears in diffs, virtual environments get tracked, and the chance of
secret leakage rises sharply.

Generate a starter from https://github.com/github/gitignore for your
language/stack, then augment with project-specific patterns.

## When to override

Never. Every Git project should have a .gitignore.
