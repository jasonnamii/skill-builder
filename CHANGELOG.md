## [1.4.0] - 2026-04-26 (베놈화)

**트리거:** 형 요청 — "스킬빌더가 신규 스킬 만들 때도 안트로픽 권장사항이 자연 발현되도록 베놈처럼 적용"

### 컨셉: 베놈 일체화
별도 모듈 없이 validate.py와 new-skill-template.md에 안트로픽 공식 권장사항 자연 합체. 외관 동일, 신규 스킬 생성 시 안트로픽 DNA 자동 발현.

### Added (validate.py — Anthropic 베놈)
- description ≤1024자 (v1.3 500자 → v1.4 1024자, Anthropic 공식 한도)
- description 모호 동사 검출 ("Helps with"·"Processes"·"Handles"·"Works with"·"Takes care of") → warning
- description 1·2인칭 검출 (3인칭/명령형 권장) → warning
- description 부정 경계 검출 (NOT:/DO NOT/except) → warning
- license 필드 권장 → warning (anthropic-skills 4개 모두 보유)
- SKILL.md ≤500줄 검사 (v1.3 KB만 → v1.4 줄수 추가, Anthropic 공식 권장)
- metrics에 `skill_md_lines` 추가

### Added (new-skill-template.md — Anthropic 발현)
- 스켈레톤에 version·license 필드 자연 포함
- description 작성 가이드: 3인칭/명령형, 모호 동사 금지 명시
- 필수 체크리스트 8행 → 16행 확장 (Anthropic 공식 항목 통합)

### Added (SKILL.md)
- frontmatter version 1.3.0 → 1.4.0 + license 필드 신설
- Lean 기준에 "≤500줄·결정적 작업 scripts/ 위임·❌WRONG/✅CORRECT 대조" 안트로픽 항목 자연 흡수
- description 작성 권고에 "모호 동사 금지·3인칭·≤1024자" 1줄 통합

### Why
- v1.3까지: 형의 로컬 룰북 (5KB·500자 등)
- v1.4 이후: 안트로픽 공식 + 로컬 룰 통합. 신규 스킬은 처음부터 안트로픽 표준 정합.
- skill-doctor v2와 양방향 정합성 확보 — skill-doctor가 진단하는 항목을 skill-builder가 처음부터 충족

---

## [1.3.0] - 2026-04-25

### Added
- **절대 규칙 #8 NO_WORK_LABEL 강제 주입** — 산출물 생성 스킬(P5에 .md/.html/.docx/.pptx/.xlsx/.pdf 포함) 신규/중간 수정 시 verbatim 블록 삽입 강제
- `references/no-work-label-block.md` — verbatim 블록 단일 진실 소스 + 자체 스캔 체크리스트 6항 + BAD/GOOD 예시
- ②-b 성능 게이트에 체크 #6 추가: `grep -q "\[NO_WORK_LABEL\]"` 자동 검증
- 신규생성 섹션에 NO_WORK_LABEL 포인터 명시
- Gotchas에 "블록 미주입·요약·변형" 함정 추가

### Why
- 작업 라벨(C:E:W:·Y2·4축·DOC_TYPE 등) 산출물 누출 = 외부 독자 차단
- 결정적 게이트(확률 ✗) — 1만 페이지 1단어 누출도 FAIL
- skill-builder 게이트 1곳 강제 = 신규/수정 모든 스킬에 자동 전파, 50+ 기존 스킬 일괄 패치 회귀위험 회피

# Changelog — skill-builder

게이트키퍼 스킬 변경이력. skill-doctor 진단·autoloop 최적화·수동 수정 모두 기록.

---

## 1.2.0 — 2026-04-21

**트리거:** 형 수동 요청 — "리서치 필요 스킬 작업 시 스킬빌더 강제 발동 + 리서치 결과 VAULT 저장 강제"

### Added
- **절대 규칙 #7 신설** — 리서치 결과 VAULT 저장 강제. 세션·`mnt/outputs/`·스크래치패드 저장 = FAIL. 저장 경로 규약: `VAULT/_skills research/{skill-name}/{YYYY-MM-DD}_{topic}.md`
- **⓵ 리서치필요 판정 섹션 신설** — PREFLIGHT 직후 배치. 판정 기준·강제 흐름·frontmatter 규약·감지 키워드 명시
- 규칙 #1 감지 조건 ⑥ 추가 — "리서치 필요 스킬 생성·수정" 강제 발동 트리거
- description P1 확장 — `리서치스킬, 리서치기반스킬` 추가
- description P3 확장 — `research-backed skill` 추가
- description P4 확장 — 도메인 리서치 선행 스킬 신설 명시
- description P5 확장 — `리서치 결과는 VAULT/_skills research/로` 명시
- Gotchas 2행 추가 — 리서치 세션 저장 함정 / WebSearch 직접 붙여넣기 함정

### Changed
- 절대 규칙 개수 6개 → 7개
- 흐름에 `ⓘ 리서치필요 판정` 단계 삽입
- description 첫줄에 리서치 강제 발동·VAULT 저장 강제 한줄 요약 추가

### Rationale
세션 종료 시 리서치 자료 전량 소실 위험. 스킬 자체는 재생성 가능하지만 리서치 원본·출처는 복구 불가. 게이트키퍼 범위를 "파일 편집"에서 "리서치 자료까지"로 확장.

---

## 1.1.0 — 2026-04-17

**트리거:** skill-doctor 진단 🟠 75.8/100 (ORANGE) → 처방 P0+P1+선택 P2 적용

### Added
- `version: 1.1.0` frontmatter 필드 (⑦-1 해소)
- `CHANGELOG.md` 신설 — 변경이력 축적 채널 (⑦-4 해소)
- `references/packaging-guide.md` 신설 — ③ 패키징 상세 스포크화 (⑤-1 해소)
- description P1에 `SKILL.md·스킬패키징·스킬검증` 복합어 추가 (⑥-2 보강)
- description P5에 `패키지로·zip으로` 추가 (②-2 보강)
- `vault_dependency` 주석 — 미마운트 시 STOP+보고 방침 명시 (④-3 보강)
- Gotchas — 패키징 실패 시 thumbs-down 피드백 + CHANGELOG 기록 경로 (⑧-3·⑧-4 보강)

### Changed
- description 첫줄 "스킬 생성·수정·패키징 게이트키퍼" → "스킬 파일 수정·생성·패키징 게이트키퍼" — 기능 암시 강화 (③-4 보강)
- P1에서 단독 `스킬`·단독 `skill` 제거 — 일반어 오발동 차단 (⑥-2 해소)
- ③ 패키징 섹션 → 4행 표 + 핵심 순서 요약. 상세는 `references/packaging-guide.md`로 이동 (⑤-1 P0 핵심)

### Metrics
- SKILL.md: 11,011B → 목표 ≤9,500B (P0 달성 확인은 validate 결과)
- 트리거 티어: P1 13→14(단독어 제거 상쇄) / P5 1→3
- 건강 점수: 75.8 → 목표 ≥85

---

## 1.0.0 — initial

초기 버전. 게이트키퍼 프로토콜 6대 절대규칙·PREFLIGHT·①~③ 선형 흐름 확립.
