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
