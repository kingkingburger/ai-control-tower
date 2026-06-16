# 코딩 선호

## TypeScript 함수 스타일

- 새로 작성하는 TypeScript helper와 export에는 arrow function을 선호한다. 특히 `export const name = async (...) => { ... }` 형태를 우선한다.
- local state를 숨기기만 하고 control flow를 읽기 어렵게 만드는 IIFE는 피한다.
- 명확한 correctness 또는 performance 이유가 없으면 module-level `let`이나 Promise cache를 피한다.
- application code에서는 `.then()`보다 `async/await`를 선호한다.
