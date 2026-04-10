# Trigger Design Guide

skill-builder 트리거 체계. SKILL.md의 description 작성 시 반드시 참조.

---

## YAML Frontmatter 규격

```yaml
---
name: my-skill          # lowercase, numbers, hyphens. max 64자
description: |          # max 500자
  [핵심 용도 1문장]
  P1: [핵심키워드 5개+].
  P2: [동사]해줘, create.
  P3: [영어 2개+].
  P5: [출력형태]로.
  NOT: [제외키워드](→대체스킬)
---
```

---

## 트리거 티어

| 티어 | 역할 | 최소 요건 | 예시 |
|------|------|----------|------|
| P1 | 고유 키워드 (명사) | 5개+ | 재무모델, financial model, 매출추정 |
| P2 | 동사 패턴 | 2개 (한+영) | 만들어줘, create |
| P3 | 영어 기술용어 | 2개+ | revenue forecast, scenario analysis |
| P4 | 상황적 표현 (선택) | 0-2개 | 작업완료후, 버전업후 |
| P5 | 출력 형태 | 1개+ | .xlsx로, .md로 |
| NOT | 제외 + 라우팅 | 필수 | 회계장부(→xlsx스킬직접) |

---

## NOT 라우팅 규칙

NOT은 단순 제외가 아니라 "이 요청은 다른 스킬이 더 적합"을 명시.

작성법: `NOT: [제외키워드](→대체스킬명)`

충돌 검사: 기존 스킬들의 description을 glob으로 읽어 P1 키워드 겹침 확인. 겹치면 NOT에 라우팅 추가.

---

## Lean 원칙

| 원칙 | 기준 |
|------|------|
| SKILL.md 크기 | 목표 5KB, 최대 10KB |
| 보조파일 | 10KB↑ 레퍼런스에 한해 허용 |
| 표 우선 | 설명 → 표로 압축 |
| 코드 최소 | 패턴만, 20줄 이내 |
| 중복 제거 | 같은 내용 1회만 |

---

## 검증 체크리스트

SKILL.md 작성 후 반드시 통과:

- [ ] YAML frontmatter 형식 (---로 시작/종료)
- [ ] name: lowercase+hyphens, 64자 이내
- [ ] description: 500자 이내
- [ ] YAML에 탭 문자 없음 (스페이스만)
- [ ] P1 5개+, P2 2개+, P3 2개+, P5 1개+, NOT 존재
- [ ] SKILL.md ≤ 10KB
- [ ] 코드블록 ≤ 20줄
- [ ] 기존 스킬과 P1 키워드 충돌 없음 (겹치면 NOT 추가)

---

## Gotchas

- description이 500자를 초과하면 YAML 파싱 에러가 아니라 트리거 성능이 저하됨
- P1에 너무 일반적인 단어(분석, 정리, 만들기)를 넣으면 오발동. 도메인 특화 명사를 우선
- NOT이 없으면 인접 스킬과 충돌 시 Claude가 임의 선택 — 반드시 명시
- P4(상황적 표현)는 선택이지만, "~후에", "~할 때" 같은 시점 트리거가 필요한 스킬에는 효과적
