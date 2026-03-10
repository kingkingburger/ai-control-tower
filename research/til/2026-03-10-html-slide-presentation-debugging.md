---
date: 2026-03-10
session: AI Native Camp 2기 HTML 슬라이드 프레젠테이션 제작 및 디버깅
source_file: research/readings/youtube/ai-native-camp-2-presentation.html
---

# TIL: HTML/CSS/JS 슬라이드 프레젠테이션 디버깅에서 배운 것들

## 1. CSS Position 관련

### `position: relative`가 `position: absolute`를 무력화하는 문제

- **상황**: 모든 `.slide`에 `position: absolute`를 걸어 뷰포트에 겹쳐 쌓은 뒤, `opacity`와 `transform`으로 전환하는 구조. `.day-header` 슬라이드만 보이지 않았다.
- **원인**: `.day-header`에 `position: relative`가 선언되어 있어, `.slide`의 `position: absolute`를 덮어썼다. CSS specificity가 아니라 cascade order(같은 specificity일 때 나중에 선언된 것이 이김) 때문에 `.day-header`의 `position: relative`가 적용됨. 결과적으로 해당 슬라이드만 normal flow에 배치되어 화면 밖으로 밀려남.
- **수정**: `.day-header`에서 `position: relative`를 제거.
- **핵심 교훈**: 슬라이드 시스템처럼 모든 요소가 반드시 `position: absolute`여야 하는 구조에서, 개별 슬라이드 스타일이 position을 재선언하면 레이아웃이 깨진다. 서브클래스에서 position 속성을 만지지 않도록 주의.

### `position: absolute` 요소도 containing block 역할을 한다

- **발견**: `position: absolute`인 부모 안의 `position: absolute` 자식도 정상 동작한다. `.day-header`에서 `position: relative`를 제거해도 내부의 절대 위치 자식 요소들이 깨지지 않았다.
- **이유**: CSS 스펙상, `position: absolute` 요소는 `position: static`이 아닌 가장 가까운 조상을 containing block으로 사용한다. `absolute` 자체가 `static`이 아니므로 containing block 역할을 충분히 수행한다. `relative`가 없어도 된다.
- **실용 규칙**: 자식에 `absolute` positioning이 필요할 때 부모에 굳이 `position: relative`를 넣을 필요 없다 -- 부모가 이미 `absolute`, `fixed`, `sticky` 중 하나이면 그 자체로 containing block이 된다.

## 2. JavaScript DOM API

### `classList.add('')`는 SyntaxError를 던진다

- **상황**: `data-group` 속성에서 색상 클래스를 꺼내 `classList.add()`에 넘기는 코드. 일부 슬라이드에 `data-group`이 없거나 매핑이 undefined일 때 빈 문자열이 전달됨.
- **에러**: `Uncaught DOMException: Failed to execute 'add' on 'DOMTokenList': The token provided must not be empty.`
- **수정**: `if (gc) dot.classList.add(gc);` -- falsy 체크로 가드.
- **핵심 교훈**: `classList.add()`, `classList.remove()`, `classList.toggle()` 모두 빈 문자열을 허용하지 않는다. 동적으로 클래스명을 생성할 때는 반드시 falsy 체크 필요. `null`, `undefined`도 마찬가지로 에러 발생.

## 3. Playwright 테스트 관련

### `file://` URL 탐색 불가

- **상황**: Playwright로 로컬 HTML 파일을 열어 슬라이드 전환을 테스트하려 함.
- **문제**: Playwright(Chromium 기반)는 `file://` 프로토콜 탐색이 제한된다.
- **우회**: Python `http.server`로 로컬 서버를 띄운 뒤 `http://localhost:PORT/` 로 접근.
- **패턴**: 로컬 HTML 테스트 시 항상 HTTP 서버 경유. `python -m http.server PORT` 한 줄이면 충분.

### `evaluate()`로 인라인 스타일 주입 시 CSS 무력화

- **상황**: Playwright의 `evaluate()`로 `slide.style.transition = 'none'`을 설정해서 애니메이션 없이 빠르게 슬라이드를 전환하려 함.
- **문제**: 인라인 스타일은 CSS specificity에서 최우선(1000점)이므로, 이후 CSS 클래스 기반 전환(`opacity`, `transform`)이 동작하지 않게 됨. 한 속성만 건드려도 side effect로 다른 속성까지 영향받을 수 있음.
- **교훈**: Playwright에서 DOM 스타일을 직접 조작할 때는 테스트 후 반드시 원복하거나, CSS 클래스 추가/제거 방식으로 제어할 것.

### 빠른 연속 탐색으로 인한 페이지 크래시

- **상황**: Playwright에서 여러 슬라이드를 빠르게 순회하며 스크린샷을 찍으려 함.
- **문제**: 페이지가 `about:blank`로 크래시. 브라우저가 이전 탐색/렌더링을 완료하기 전에 다음 명령이 들어오면 페이지 상태가 불안정해짐.
- **교훈**: Playwright 자동화에서 순차적 DOM 조작 시, 각 단계 사이에 적절한 대기(`waitForSelector`, `waitForTimeout`)를 넣어야 한다. 특히 CSS transition이 있는 UI에서는 transition duration 이상의 대기가 필요.

## 4. Reusable Patterns

| 패턴 | 설명 | 적용 시점 |
|------|------|----------|
| **Guard before classList** | `classList.add/remove/toggle`에 동적 값을 넘기기 전 falsy 체크 | DOM 클래스 동적 조작 시 항상 |
| **HTTP server for local HTML** | `python -m http.server`로 로컬 파일에 HTTP 접근 | Playwright, CORS, Service Worker 등 file:// 제한 상황 |
| **Position inheritance 인식** | `absolute` 부모는 그 자체로 containing block -- `relative` 불필요 | CSS 레이아웃 설계 시 |
| **Inline style 주의** | Playwright evaluate로 인라인 스타일 주입 시 CSS 클래스 동작 무력화 가능 | E2E 테스트에서 스타일 조작 시 |
| **Sequential Playwright ops** | 빠른 연속 조작 대신 waitFor 패턴으로 안정적 순차 실행 | Playwright 자동화 전반 |
