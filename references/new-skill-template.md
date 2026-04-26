# 신규 스킬 템플릿

새 스킬 생성 시 이 스켈레톤에서 시작. 필수 구조를 빠뜨리지 않기 위한 가이드.

---

## SKILL.md 스켈레톤

```markdown
---
name: {skill-name}
version: 1.0.0
license: Proprietary. LICENSE.txt has complete terms
description: |
  {핵심 용도 1문장. 3인칭/명령형으로. "Helps with"·"Processes"·"Handles" 같은 모호 동사 금지.}
  P1: {고유 명사 키워드 5개+, 쉼표 구분}.
  P2: {동사 패턴 한+영 2개+}.
  P3: {영어 기술용어 2개+}.
  P4: {상황적 표현 0-2개. 선택}.
  P5: {출력 형태 1개+}.
  NOT: {제외 키워드}(→{대체 스킬}).
---

# {Skill Name}

{스킬의 핵심 가치 1줄}

---

## 절대 규칙

| # | 규칙 | 이유 |
|---|------|------|
| 1 | {가장 중요한 규칙} | {왜 필요한지} |

---

## 실행 흐름

```
① {Phase 1} → ② {Phase 2} → ③ {Phase 3}
```

### ① {Phase 1}

{절차 설명}

### ② {Phase 2}

{절차 설명}

### ③ {Phase 3}

{절차 설명}

---

## Gotchas

| 함정 | 대응 |
|------|------|
| {실패 패턴 1} | {대응 방법} |
| {실패 패턴 2} | {대응 방법} |
```

## 필수 체크리스트 (Anthropic 공식 베놈 + 로컬 룰)

| 항목 | 근거 |
|------|------|
| YAML frontmatter 있음 | validate.py 파싱 필수 |
| name: `^[a-z0-9-]{1,64}$` | Anthropic 공식 형식 |
| version 필드 | 변경이력 추적 |
| license 필드 | Anthropic 권장 (anthropic-skills 4개 모두 보유) |
| description ≤1024자 | Anthropic 공식 한도 (≤900자 권장) |
| description 3인칭/명령형, 모호 동사 금지 | Anthropic 권장 ("Helps with"·"Processes"·"Handles" 금지) |
| description 부정 경계 (NOT/DO NOT/except) | cascade 명확성 |
| P1 5개+, P2 2개+, P3 2개+, P5 1개+, NOT 필수 | 트리거 최소 요건 |
| Gotchas 섹션 있음 | Lean 원칙: Gotchas 필수 |
| ❌WRONG/✅CORRECT 대조 1개+ | xlsx·docx 표준 패턴 (피드백 강화) |
| Quick Reference 도입부 (첫 100줄 내) | 학습곡선 완화 (Anthropic 권장) |
| SKILL.md ≤10KB·≤500줄 | 토큰 예산 + Anthropic 공식 |
| 결정적 작업(검증·계산·파싱) → scripts/ 위임 | LLM 강요 안티패턴 차단 (Anthropic 권장) |
| "왜" 있음 | 이유 없는 지시 → LLM이 무시 |
| 예시 1개+ | 없으면 출력 자의적 |
| CHANGELOG.md 신설 | 버전관리 |

## 폴더 구조

```
{skill-name}/
├── SKILL.md          (필수)
├── references/       (5KB+ 시 분리)
├── scripts/          (결정적·반복 작업)
└── assets/           (출력용 파일)
```

## NOT 설계 팁

NOT은 "이 요청은 다른 스킬이 더 적합"을 명시하는 라우팅.
기존 스킬 P1 키워드와 겹치는 게 있으면 반드시 NOT에 추가.
형식: `NOT: {키워드}(→{스킬명})`
