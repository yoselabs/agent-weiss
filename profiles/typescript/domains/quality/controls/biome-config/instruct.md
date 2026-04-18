# Why biome

Biome is the fast Rust replacement for ESLint + Prettier. One tool, one
config, sub-second runs even on large codebases.

For agents: a single config file (vs. ESLint's plugin-soup) means less
context to load when the agent needs to understand the project's style.

## How to add

```bash
npm install --save-dev --save-exact @biomejs/biome
npx @biomejs/biome init
```

This creates `biome.json` with sensible defaults. Customize as needed.

## Override

Teams committed to ESLint+Prettier (often for legacy plugin compatibility)
may declare an override referencing their existing config.
