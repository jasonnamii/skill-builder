---
name: skill-builder
description: |
  스킬 생성·수정·패키징 유일한 게이트키퍼. SKILL.md를 수정하기 전 반드시 Skill tool로 발동. 스킬 진단·리팩터링·재작성·트리거설계·Lean작성·검증·성능게이트·.skill 패키징 전 과정 수행.
  P1: 스킬, skill, SKILL.md, 패키징, 검증, 스킬만들기, 스킬수정, 스킬고치기, 스킬리팩터링.
  P2: 만들어줘, 수정해줘, 고쳐줘, 재작성해줘, validate, create, fix, refactor.
  P3: skill creation, skill modification, skill refactoring, description optimization.
  P4: SKILL.md를 편집하려 할 때, 스킬 파일을 수정하려 할 때, 스킬 구조를 변경하려 할 때.
  P5: .skill로.
  NOT: 프롬프트엔지니어링(→직접), 플러그인(→create-cowork-plugin), 스킬최적화루프(→autoloop), 다른 스킬 단순 사용(→해당 스킬).
---

# Skill Builder

스킬 생성·수정·패키징. 선형 흐름 — 분기 최소, 루프 0.

---

## ⛔ 절대 규칙 (5개)

| # | 규칙 | 이유 |
|---|------|------|
| 1 | **게이트키퍼** — SKILL.md 수정·생성 전 **반드시 `Skill tool`로 skill-builder 발동**. 도구 무관. 미발동 수정 = FAIL | 진단→수정 전환 시 발동 누락이 가장 흔한 위반 |
| 2 | **수정 완료 = .skill 패키징 제공** | 사용자가 설치할 수 없음 |
| 3 | **작업대 = 볼트 `_Skills archive/`** — FS로 편집. Cowork Read/Edit는 폴백. **재시도 루프 금지** | FS로 볼트 직접 작업이 빠르고 영속적 |
| 4 | **루프 하드캡** — 모든 재시도·검증 순회 **max 2회**. 초과 → 보고 + STOP | 무한 루프 방지 |
| 5 | **원본 유일 = skills-plugin** — 작업대(`_Skills archive/`)는 **순수 편집 공간**. 여기서 git-sync·배포·참조·수정소스 사용 = FAIL. 매번 원본에서 새로 가져와야 한다. 반영은 형이 .skill 설치로 직접 수행 | 작업대 잔해가 원본으로 오염되면 버전 꼬임 |

---

## 실행 흐름 — 선형 3단계

```
① 읽기+판정 → [진단이면 보고+종료] → ② 편집 → ②-b 검증+성능게이트 → ③ 패키징+제공
```

### ① 읽기 + 경로 판정

```
WORKBENCH = $HOME/Library/CloudStorage/Dropbox/ObsidianVault/Agent-Ops/_Skills archive/
ORIGIN = skills-plugin 경로 (mnt/.claude/skills/ 로 접근)

1. 원본(ORIGIN)에서 WORKBENCH로 FS 복사:
   FS read_file(ORIGIN/{skill}/SKILL.md) → FS write_file(WORKBENCH/{skill}/SKILL.md)
   ⚠ WORKBENCH에 이전 작업 잔해가 있으면 무시하고 원본으로 덮어쓴다
2. SKILL.md 읽기 (FS read_file)
3. python scripts/validate.py (세션에 복사 후 실행 — validate만 세션에서)
4. 경로 판정 (1회 확정):
   - 진단: "진단해줘/검증해줘" 요청 → validate.py 결과 보고만. ②③ 스킵, 종료. 이후 "수정하자" 시 Skill tool 재발동 필수
   - 경미: 수정 개소 ≤3, 섹션 구조 동일
   - 중간: 섹션 신설·삭제·재배치, 로직 변경
   - 신규: 처음부터 만듦
```

**N개 동시 처리:** 독립 스킬이면 FS 복사 + Read + validate.py를 병렬 tool call로 발행.

### ② 편집

| 경로 | 할 일 | 도구 |
|------|-------|------|
| 경미 | 해당 부분만 수정. description 변경 필요 시 같은 턴에 갱신. **검증: validate.py만. 성능 게이트: 스킵** | FS edit_file |
| 중간 | 구조 변경 + description 갱신 → ②-b 검증+성능게이트 | FS edit_file 또는 FS write_file |
| 신규 | 의도→트리거→SKILL.md 작성 → ②-b 검증+성능게이트 | FS write_file |

**편집 대상 경로:** WORKBENCH(`_Skills archive/{skill}/`). FS MCP 불가 시 Cowork Edit/Write 폴백.

### ②-b 검증 + 성능 게이트 (중간+신규)

편집 완료 후, 패키징 전에 반드시 통과.

**검증 (코드 자동화):**
```bash
# WORKBENCH에서 세션으로 복사 후 실행 (validate는 세션 샌드박스에서)
cp -r "{WORKBENCH}/{skill}/" ./{skill}/ 2>/dev/null; chmod -R u+w ./{skill}/
python scripts/validate.py ./{skill}/
# errors=[] → 통과. errors 있으면 WORKBENCH 수정 후 재복사+1회 재실행.
# 2회차 실패 → STOP + 보고
```

**성능 게이트:** `→ references/perf-checklist.md 참조`
**속도 저하 원인 + 트레이드오프 금지선:** `→ references/perf-checklist.md §실행 속도 저하 7대 원인 / §속도 vs 품질 트레이드오프 금지선 참조`

| # | 체크 | 자동화 |
|---|------|--------|
| 1 | 허브스포크 (허브=분기·규칙·포인터만, 스포크=세부를 references/로 분리) | validate.py → `hub_spoke` 필드 |
| 2 | 불필요 로딩 방지 | @uses vs 본문 `→ references/` 포인터 비교 |
| 3 | 코드 대체 가능성 | validate.py → `automatable_sections` |
| 4 | 토큰 예산 | validate.py → `combined_tokens_estimate` (>30K 경고) |
| 5 | 병목 구간 식별 | validate.py → `phases_count` + 텍스트 비중 |

### ③ 패키징 + 제공

```bash
# WORKBENCH → 세션으로 최종본 복사 후 zip
WORKBENCH="$HOME/Library/CloudStorage/Dropbox/ObsidianVault/Agent-Ops/_Skills archive"
rm -rf /sessions/{session-id}/{skill-name}/
cp -r "{WORKBENCH}/{skill-name}/" /sessions/{session-id}/{skill-name}/
rm -f /sessions/{session-id}/{skill-name}.skill
cd /sessions/{session-id}
zip -r /sessions/{session-id}/{skill-name}.skill {skill-name}/ \
  -x "*.pyc" -x "__pycache__/*" -x ".DS_Store" -x ".git/*" -x "*-workspace/*" -x "evals/*"
```

```
mcp__cowork__present_files([{"file_path": "/sessions/{session-id}/{skill-name}.skill"}])
```

**재패키징:** outputs에 기존 .skill → 형에게 삭제 확인 → allow_cowork_file_delete → 재패키징.
**git-sync:** 패키징 완료 후 "git push 할까요?" 1줄 제안. 형 컨펌 시 git-sync 발동.

---

## 허브스포크 판정

**판정 시점:** ① 읽기 단계에서 `validate.py` 자동 판정. 전환도 1회만.

| 조건 (하나라도) | 결과 |
|----------------|------|
| validate.py → `hub_spoke: "recommended"` | 허브스포크 전환 제안 |
| SKILL.md >5KB + references/ 있음 (`hub_spoke: "yes"`) | 이미 허브스포크. 포인터 정합성 확인 |
| 단일인데 10KB 근접 또는 섹션 6개+ | 허브스포크 전환 |
| 해당 없음 (`hub_spoke: "no"`) | 단일 유지 |

**허브:** 분기·규칙·포인터만. 목표 3KB, 최대 5KB. 세부는 `references/`로 분리.
**스포크:** 경로별 절차, 스키마, 도메인 지식 등 필요 시에만 로딩.
**포인터:** `→ references/{파일명}.md 참조`

---

## 신규생성 — 트리거 설계

`→ references/trigger-guide.md 참조`

| 티어 | 역할 | 최소 |
|------|------|------|
| P1 | 고유 키워드 (명사) | 5개+ |
| P2 | 동사 패턴 | 2개 (한+영) |
| P3 | 영어 기술용어 | 2개+ |
| P4 | 상황적 표현 | 0-2 (선택) |
| P5 | 출력 형태 | 1개+ |
| NOT | 제외 + 라우팅 | 필수 |

**description은 적극적으로** — Claude는 스킬을 덜 쓰는 쪽으로 편향. 범위를 넓혀라.

## 신규생성 — Lean 작성

| 원칙 | 기준 |
|------|------|
| SKILL.md 크기 | 목표 5KB, 최대 10KB |
| 표 우선 | 설명 → 표로 압축 |
| 코드 분리 | 결정적·반복적 작업 → scripts/로. SKILL.md에는 패턴만 |
| 중복 제거 | 같은 내용 1회만 |
| "왜" 필수 | 이유 없는 지시 → LLM이 무시함 |
| 예시 1개+ | 없으면 출력 자의적 |
| Gotchas 필수 | 실패 패턴 명시 |

**예시 — Lean 적용 Before/After:**
```
Before (비효율):                    After (코드화):
  ## 검증 체크리스트                   python scripts/validate.py ./{skill}/
  - YAML `---` 확인                  → JSON {valid, errors, metrics}
  - name kebab-case 확인             → 동일 검증을 코드 1회 호출
  - description 500자 확인           → ~50 토큰 (vs 텍스트 ~500)
  → LLM이 매번 텍스트로 판단
```

```
스킬 구조:
skill-name/
├── SKILL.md          (필수)
├── references/       (필요시 로딩)
├── scripts/          (결정적·반복적 작업 코드화)
└── assets/           (출력용 파일)
```

---

## 배치 모드

2개+ 스킬 동시 요청 시: 같은 단계끼리 묶어 병렬 발행.

```
Read(A)+Read(B) → Edit(A)+Edit(B) → zip A & zip B & wait → present_files
```

---

## Gotchas

| 함정 | 대응 |
|------|------|
| mnt/.claude/skills/ 직접 쓰기 | 읽기전용. WORKBENCH로 복사 후 편집 → .skill 설치만 반영 |
| `/tmp/` 경로 | Read/Edit 접근 불가. 세션 디렉토리만 사용 |
| **작업대(`_Skills archive/`)에서 git-sync·배포·참조** | **FAIL. 작업대는 순수 편집 공간. 원본(skills-plugin)만이 git-sync·배포 소스. 작업대 잔해로 시작하지 말 것 — 매번 원본에서 가져와라** |
| description↔본문 불일치 | description이 발동 판단 유일 입력. 수정 시 동기 확인 |
| zip 대신 tar | .skill은 zip만. tar = 설치 실패 |
| FS MCP 집착 / 순차 처리 | FS 불가 → Cowork 즉시 진행. 독립 스킬은 병렬 tool call |
| SKILL.md 2개 | zip 전 `find {skill}/ -name "SKILL.md" \| wc -l`로 1개 확인 |
| 진단→수정 전환 시 발동 누락 | "그럼 수정하자"로 넘어갈 때 **Skill tool 호출 먼저** |
