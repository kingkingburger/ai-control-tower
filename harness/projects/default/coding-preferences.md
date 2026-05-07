# Coding Preferences

## TypeScript Function Style

- Prefer arrow functions for newly written TypeScript helpers and exports, especially `export const name = async (...) => { ... }`.
- Avoid IIFEs when they only hide local state and make the control flow harder to read.
- Avoid module-level `let` or Promise caches unless there is a clear correctness or performance reason.
- Prefer `async/await` over `.then()` in application code.
