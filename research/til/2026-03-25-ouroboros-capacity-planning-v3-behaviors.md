---
date: 2026-03-25
session: 삼성중공업 Capacity Planning Simulation Ouroboros 문서 세트 작성
---

# TIL: Ouroboros v3 엔진의 35개 내장 Behavior와 JSON 기반 조선소 시뮬레이션

## 1. Technical Learnings

### Ouroboros v3 엔진: 코드 없이 JSON만으로 시뮬레이션 가능

- **발견**: v3 엔진에 bundle, assemble, branch, acquire_resource 등 **35개 behavior가 이미 구현**되어 있다.
- **의미**: 새로운 파이썬 코드를 작성하지 않고도 JSON 설정만으로 복잡한 조선소 시뮬레이션을 구축할 수 있다.
- **규칙**: Ouroboros 시뮬레이션 구축 시 먼저 내장 behavior 목록을 확인하고, 없는 것만 커스텀 작성한다.

### Bundle vs Assemble: 같은 포트 N개 vs 다른 포트 각각

| 용어 | 의미 | JSON 복잡도 | 사용 케이스 |
|------|------|-----------|----------|
| **Bundle** | 같은 포트에 N개 Entity 동시 수용 | 단순 | 단순 병렬 처리 |
| **Assemble** | 다른 포트 각각에 Entity 배치 | 복잡 | 실제 조립 공정 |

- **발견**: assemble이 상위호환이지만 bundle이 JSON 설정이 훨씬 단순하다.
- **규칙**: 포트 분리가 필요 없으면 bundle을 먼저 시도하고, 라우팅 분기가 필요하면 assemble로 전환한다.

### Entity 추적 및 라우팅: contents와 tags 속성

- **Entity.contents**: Lot(작업 단위)을 추적한다. Lot의 생명주기(진입→가공→출발)를 tags로 마킹할 수 있다.
- **Entity.tags**: 라우팅 분기 조건으로 사용된다. 예: `tags: ["rush", "standard"]` → 우선순위 결정.
- **규칙**: 복잡한 라우팅이 필요하면 Entity 설계 시 tags 스키마를 먼저 정의하고, Process에서 branch behavior로 분기한다.

### Process vs Product: 삼성중공업의 원래 요구사항

- **Process**: 공정(작업 순서, 우선순위, 라우팅). Behavior tree로 표현.
- **Product**: Entity의 Merge(여러 Lot을 하나로), ID 변환(구분 호출명→블록명). 상태 변환.
- **발견**: 최초 요구사항은 공정 라우팅(Process) + 블록 ID 변환(Product)이었다. 문서화할 때 이 두 축을 명확히 분리해야 한다.
- **규칙**: Ouroboros 시뮬레이션 문서는 항상 "(1) Process 구조", "(2) Product 데이터 모델" 두 섹션으로 나눈다.

### MCP Obsidian 등록: ~/.claude.json vs ~/.claude/mcp.json

- **발견**: mcp-obsidian이 `~/.claude/mcp.json`에서 로드되지 않는다. 대신 `~/.claude.json` (user 스코프)에 등록해야 한다.
- **원인**: Claude Code의 MCP 로딩 우선순위: `~/.claude.json` (user) > `.claude.json` (project) > `~/.claude/mcp.json` (legacy).
- **해결 패턴**:
  ```bash
  claude mcp add -s user mcp-obsidian
  ```
  이 명령어로 `~/.claude.json`에 등록된다.
- **규칙**: MCP 등록 후 동작하지 않으면 `~/.claude.json` 존재 여부와 MCP 이름을 먼저 확인한다.

### 삼성중공업 비교검증 계획: NSL의 Simio/DEVS

- **발견**: 서경민 CTO가 NSL(국방과학연구소)에서 Simio(상용 시뮬레이션 도구) 및 DEVS(Discrete Event System Specification) 기반 시뮬레이션과 Ouroboros 결과를 비교검증할 예정이다.
- **의미**: Ouroboros 결과의 신뢰성 검증이 진행되고 있다는 신호. 부정확한 behavior 구현이 발견될 수 있다.
- **규칙**: 문서화 완료 후 검증 결과를 기다리고, 발견된 오류는 behavior 수정 및 문서 반영으로 진행한다.

## 2. Workflow Patterns (잘 된 것)

### v3 엔진 문서와 코드 동시 분석

원래 요구사항(Process + Product)을 먼저 파악한 후 v3 엔진의 기존 behavior를 매핑하는 방식이 효율적이었다. 새 기능을 작성하기 전에 기존 기능 목록을 확인하는 단계가 중요하다.

### Entity 설계 → Process 구조 → JSON 설정의 순서

복잡한 시뮬레이션일수록 먼저 Entity 모델(Lot, Block, Port)을 정의하고, 그 다음 Process 흐름(bundle/assemble/branch)을 설계한 후, 마지막에 JSON으로 인스턴스화하는 순서를 지키면 오류가 적다.

## 3. Mistakes & Inefficiencies (개선점)

### MCP Obsidian 동작 불가 문제를 늦게 인지

- 처음에 `~/.claude/mcp.json`에 등록하려고 시도했고, 동작하지 않자 설정 오류를 의심했다.
- 올바른 위치는 `~/.claude.json`(user 스코프)이었다.
- **개선**: MCP 로딩 실패 시 경로 우선순위를 먼저 확인한다.

### 새로운 Behavior 개발을 먼저 가정

- 조선소 시뮬레이션이 특수하다고 생각해서 새 코드가 필요하다고 가정했다.
- 실제로는 v3 엔진에 35개 behavior가 이미 있었다.
- **개선**: 새 기능 개발 전에 `behavior/` 디렉토리를 전체 확인하고, 기존 behavior 조합으로 가능한지 먼저 검토한다.

## 4. Reusable Patterns (향후 적용)

| 패턴 | 설명 | 적용 시점 |
|------|------|----------|
| **JSON 기반 설정 우선** | 새 코드 작성 전 내장 behavior 목록 확인 | Ouroboros 시뮬레이션 구축 시 |
| **bundle → assemble 전환** | 단순한 경우 bundle로 시작, 라우팅 분기 필요 시 assemble로 확장 | 공정 설계 초기 단계 |
| **Entity 모델 먼저 정의** | contents(Lot 추적) + tags(라우팅) 스키마를 Process보다 먼저 설계 | 복잡한 시뮬레이션 |
| **Process + Product 분리 문서화** | 공정 구조와 데이터 모델을 항상 별도 섹션으로 작성 | Ouroboros 시뮬레이션 문서 작성 |
| **MCP 로딩 경로 확인** | 등록 실패 시 `~/.claude.json` → `.claude.json` → `~/.claude/mcp.json` 순서 확인 | MCP 동작 불가 시 |
| **검증 계획 추적** | 상용 도구(Simio/DEVS)와의 비교검증 결과를 문서에 반영할 준비 | 시뮬레이션 결과 발행 전 |

## 5. 다음 단계 (Next Session)

1. Ouroboros v3 엔진의 35개 behavior 전체 목록을 문서화하고, 각각의 JSON 스키마를 작성한다.
2. 삼성중공업 조선소 시뮬레이션의 Entity 모델(Lot, Block, Port, Stage)을 확정하고, 문서에 다이어그램으로 표현한다.
3. 서경민 CTO의 Simio/DEVS 비교검증 결과를 추적하고, 발견된 오류가 있으면 behavior 수정 및 문서 업데이트를 준비한다.
4. 실제 조선소 데이터(작업 시간, 포트 용량)를 JSON 설정에 반영하는 과정을 문서화한다.
