# Hub-Spoke 전환 절차

단일 SKILL.md → 허브스포크 구조로 전환할 때의 구체적 절차.

---

## 판정 기준 (validate.py 자동)

| 조건 | 결과 |
|------|------|
| hub_spoke: "recommended" | 전환 대상 |
| SKILL.md >5KB + references/ 없음 | 전환 필요 |
| 섹션 6개+ 또는 10KB 근접 | 전환 권장 |

## 전환 절차

### 1. 분리 대상 식별

허브에 남길 것과 스포크로 빼낼 것을 구분:

| 허브 (SKILL.md) | 스포크 (references/) |
|-----------------|---------------------|
| 절대 규칙 | 경로별 상세 절차 |
| 실행 흐름 요약 | 도메인 지식 |
| 분기 판정 기준 | 예시·Before/After |
| Gotchas (요약) | 상세 체크리스트 |

**원칙:** 허브는 "무엇을 할지" 판단하는 데 필요한 최소 정보. 스포크는 "어떻게 할지" 세부.

### 2. 스포크 파일 생성

```
references/
├── {기능명}.md          # 예: hub-spoke-guide.md
├── {절차명}.md          # 예: perf-checklist.md
└── {도메인지식명}.md     # 예: trigger-guide.md
```

**네이밍:** kebab-case, 내용을 2~3단어로 요약. 확장자 .md 필수.

### 3. 포인터 작성

허브에서 스포크를 참조하는 포인터 형식:

```
**상세 절차:** → references/hub-spoke-guide.md 참조
```

**규칙:**
- `→` 기호 필수 (validate.py가 이것으로 포인터 감지)
- 파일명은 정확히 일치 (대소문자 포함)
- 한 줄에 하나의 포인터

### 4. 허브 크기 검증

| 항목 | 목표 | 최대 |
|------|------|------|
| 허브 크기 | 3KB | 5KB |
| 스포크 개별 | 3KB | 5KB |
| 합산 토큰 | <20K | <30K |

### 5. 포인터 정합성 검증

```bash
python scripts/validate.py ./{skill}/
# broken_ref_pointers: [] 이면 통과
```

## Gotchas

| 함정 | 대응 |
|------|------|
| 분리 후 허브에 세부가 남음 | 허브 재검토 — "이걸 안 읽어도 판단할 수 있나?" 질문 |
| 포인터 오타 | validate.py → broken_ref_pointers로 자동 감지 |
| 스포크끼리 순환 참조 | 스포크→스포크 참조 금지. 허브가 유일한 진입점 |
| 전환 후 description 미갱신 | 허브스포크 전환 시 description도 함께 갱신 |
