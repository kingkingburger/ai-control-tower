# 멀티 에이전트 오케스트레이션 패턴

Claude Code에서 멀티 에이전트 워크플로우를 설계할 때 쓰는 상세 패턴.

## 핵심 원칙

> **"에이전트 아키텍처는 작업의 의존성 그래프를 반영해야 한다"**
> — Anthropic 멀티 에이전트 연구(Anthropic Multi-Agent Research)

하위 작업이 서로의 상태를 읽거나 수정하지 않으면 **병렬**로 실행한다.
앞 단계의 출력이 다음 단계의 입력이면 **순차**로 실행한다.

## 병렬 vs 순차 결정 기준

| 조건 | 권장 패턴 |
|------|-----------|
| 하위 작업이 독립적임(공유 상태 없음) | **병렬** |
| 이전 단계 출력이 다음 단계 입력임 | **순차** |
| 다양한 관점/전문성이 필요함 | **병렬**(fan-out) |
| 결과의 응집성/일관성이 중요함 | **순차** |
| 실행 전 제안 검증이 필요함 | **2단계**(생성→검증) |

## Anthropic의 6가지 조합형 패턴

| 패턴 | 설명 | 사용 시점 |
|------|------|-----------|
| **Prompt Chaining** | 각 출력이 다음 입력이 되는 순차 단계 | 데이터 변환 pipeline |
| **Routing** | 입력 타입에 따라 전문 에이전트로 분기 | 다중 도메인 처리 |
| **Parallelization** | 독립 작업을 동시에 실행 | 다각도 분석, 속도 최적화 |
| **Orchestrator-Worker** | 동적 작업 배정 | 복잡한 코딩/리서치 |
| **Evaluator-Optimizer** | 생성→평가 반복 루프 | 품질 개선이 필요할 때 |
| **Autonomous Agent** | 최소 개입, 환경 feedback 기반 | 장시간 실행 작업 |

## 2단계 pipeline 패턴

검증이 필요한 제안을 생성하는 워크플로우에 사용한다.

```
Phase 1: 분석/생성(병렬)
┌──────────┬──────────┬──────────┐
│ Agent A  │ Agent B  │ Agent C  │  ← 독립 분석
└────┬─────┴────┬─────┴────┬─────┘
     │          │          │
     └──────────┼──────────┘
                ↓
Phase 2: 검증(순차)
┌─────────────────────────────────┐
│         Validator Agent         │  ← Phase 1 결과 검증
└─────────────────────────────────┘
```

### 적용 예시

**세션 마무리 워크플로우:**
- Phase 1: doc-updater, automation-scout, learning-extractor, followup-suggester(병렬)
- Phase 2: duplicate-checker(순차)

**코드 리뷰 워크플로우:**
- Phase 1: security-reviewer, style-checker, performance-analyzer(병렬)
- Phase 2: final-reviewer(순차)

**리서치 워크플로우:**
- Phase 1: source-finder, fact-checker, perspective-gatherer(병렬)
- Phase 2: synthesizer(순차)

## 상태 관리 원칙

```
❌ 피할 것:
- 동시 실행 에이전트 사이에 mutable state 공유
- 에이전트 경계 너머 업데이트가 동기식이라고 가정
- 명시적 확인 없이 독립성을 가정

✅ 권장:
- 에이전트를 가능한 한 격리
- output_key로 상태를 명시적으로 전달
- 결과 통합을 위한 충돌 해결 전략 정의
- 전체 데이터가 아니라 가벼운 참조 전달
```

## 안티패턴

| 안티패턴 | 문제 | 대안 |
|----------|------|------|
| 의미 없는 에이전트 추가 | 복잡도만 증가 | 단일 에이전트로 충분한지 먼저 확인 |
| 과도한 multi-hop 통신 | 지연 증가 | 직접 통신 또는 병렬화 |
| 불명확한 작업 경계 | 중복 작업과 빈틈 발생 | 목표, 출력 형식, 경계를 명확히 정의 |
| 경직된 계획 고수 | 런타임 발견에 적응 불가 | adaptive orchestrator 사용 |

## 에이전트 모델 선택

| 사용 사례 | 권장 모델 |
|-----------|-----------|
| 깊이가 필요한 분석 | `sonnet` 또는 `opus` |
| 빠른 검증 | `haiku` |
| 부모 설정 기본값/상속 | `inherit` |
| 창의적/복잡한 추론 | `opus` |
| 비용 민감 batch 작업 | `haiku` |

## Claude Code에서 구현

### 병렬 실행

여러 Task 호출을 하나의 메시지로 보낸다.

```python
# 4개 에이전트가 동시에 시작
Task(subagent_type="agent-a", prompt="...")
Task(subagent_type="agent-b", prompt="...")
Task(subagent_type="agent-c", prompt="...")
Task(subagent_type="agent-d", prompt="...")
```

### 순차 실행

다음 호출 전에 이전 결과를 기다린다.

```python
# 첫 번째 호출
result_1 = Task(subagent_type="agent-a", prompt="...")

# 다음 호출에서 result_1 사용
Task(subagent_type="agent-b", prompt=f"Validate: {result_1}")
```

### 하이브리드(2단계)

```python
# Phase 1: 병렬
Task(subagent_type="analyzer-1", prompt="...")
Task(subagent_type="analyzer-2", prompt="...")
Task(subagent_type="analyzer-3", prompt="...")

# Phase 1 결과를 모두 기다림

# Phase 2: 순차(Phase 1 결과 사용)
Task(
    subagent_type="validator",
    prompt=f"""
    Validate these proposals:

    Analyzer 1: {result_1}
    Analyzer 2: {result_2}
    Analyzer 3: {result_3}
    """
)
```

## 멀티 에이전트 시스템용 에이전트 설계

### 명확한 경계

각 에이전트는 다음을 가져야 한다.
- **단일 책임**: 하나의 명확한 초점 영역
- **정의된 입력**: 무엇을 받을지에 대한 기대값
- **구조화된 출력**: downstream에서 소비하기 쉬운 일관된 형식
- **부작용 없음**: 다른 에이전트가 의존하는 상태를 수정하지 않음

### 커뮤니케이션 프로토콜

```markdown
## 에이전트 출력 형식

### 요약
[한 줄 요약]

### 상세 발견 사항
[구조화된 분석]

### 권고 사항
[우선순위가 있는 실행 항목]

### 신뢰도
[분석 품질 자체 평가]
```

## 확장 고려사항

### 에이전트를 더 추가할 때

✅ 추가해도 되는 경우:
- 구분되는 전문 영역이 필요함
- 독립 분석이 가능함
- 명확한 경계를 정의할 수 있음
- 단일 에이전트보다 복잡도를 낮춤

❌ 추가하지 말아야 하는 경우:
- 기존 에이전트와 같은 전문성
- 강한 결합을 만들 가능성
- 단순 프롬프트 수정으로 충분함
- 가치 없이 지연만 늘림

### 성능 최적화

1. **Phase 2 에이전트 최소화**: 검증은 가벼워야 함
2. **Phase 1 크기 조정**: 보통 병렬 에이전트 3-5개가 적절함
3. **검증에는 haiku 사용**: 빠르고 저렴하며 확인에 충분함
4. **가능하면 batch 처리**: 관련 분석을 단일 에이전트에 묶음

## 참고 자료

- [Anthropic Multi-Agent Research](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Azure AI Agent Design Patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- [Building AI Agents - Evaluator-Optimizer Pattern](https://research.aimultiple.com/building-ai-agents/)
