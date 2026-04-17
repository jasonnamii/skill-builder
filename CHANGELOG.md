# Changelog — skill-builder

게이트키퍼 스킬 변경이력. skill-doctor 진단·autoloop 최적화·수동 수정 모두 기록.

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
