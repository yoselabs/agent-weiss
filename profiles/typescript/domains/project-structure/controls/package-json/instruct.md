# Why package.json conventions matter

A well-formed `package.json` is the project's machine-readable spec.

- **`"type": "module"`** declares ESM. Without it, Node treats `.js` as
  CJS, breaking modern `import` syntax silently or noisily depending on
  context. (Modern TS projects should always be ESM.)
- **`engines.node`** locks the minimum Node version. Without it, a
  developer or CI on an old Node sees mysterious runtime errors instead
  of a clean "your Node is too old."
- **No wildcard versions (`"*"`)** in dependencies. Wildcards accept
  anything, including breaking majors. `npm install` returns different
  versions each time, making bugs non-reproducible.

## How to fix

```json
{
  "name": "my-project",
  "type": "module",
  "engines": { "node": ">=22" },
  "dependencies": {
    "some-lib": "^1.2.3"
  }
}
```

## Override

Pure-CJS legacy packages (rare in 2026) may override the `"type": "module"`
rule with a documented reason. Wildcard versions never have a legitimate
override — pin them.
