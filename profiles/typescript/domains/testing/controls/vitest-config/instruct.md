# Why vitest

Vitest replaces Jest for modern TS projects: native ESM, sub-second cold
starts, identical-API test files, and Vite-driven HMR for test reruns.
For projects already using Vite, Vitest reuses the same config and
plugin chain.

For agents: a Vitest config file is the unambiguous "tests live here, run
them with `npx vitest`" signal.

## How to add

Minimal `vitest.config.ts`:
```ts
import { defineConfig } from 'vitest/config';
export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
  },
});
```

## Override

Projects on Jest, ava, or other runners may declare an override referencing
the existing tool.
