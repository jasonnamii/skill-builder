---
name: skill-builder
description: |
  스킬 생성·수정·패키징 게이트키퍼. PREFLIGHT·진단·리팩터링·트리거설계·검증·성능게이트·.skill 패키징. autoloop handoff 지원.
  P1: 스킬, skill, SKILL.md, 패키징, 검증, 스킬수정, 스킬생성, 스킬고도화.
  P2: 만들어줘, 수정해줘, 고쳐줘, 재작성, validate, create, fix, refactor.
  P3: skill creation, skill modification, skill refactoring.
  P4: SKILL.md 편집, references 수정, autoloop 완료, EDIT4 대상=SKILL.md, {스킬명} 수정 감지.
  P5: .skill로.
  NOT: 프롬프트엔지니어링(→직접), 플러그인(→create-cowork-plugin), 스킬최적화루프(→autoloop).
vault_dependency: HARD
---

# Skill Builder

스킬 생성·수정·패키징. 선형 흐름 — 분기 최소, 루프 0.

---

## ⛔ 절대 규칙 (6개)

| # | 규칙 | 이유 |
|---|------|------|
| 1 | **게이트키퍼** — SKILL.md 수정·생성 전 **반드시 `Skill tool`로 skill-builder 발동**. 도구 무관. 미발동 수정 = FAIL | 진단→수정 전환 시 발동 누락이 가장 흔한 위반 |
| 2 | **수정 완료 = .skill 패키징 제공** | 사용자가 설치할 수 없음 |
| 3 | **세션 내 직접 편집** — 원본(ORIGIN)을 세션으로 복사 → Cowork Edit/Write로 수정 → zip → present. FS MCP는 plugin_skills_path 반영 시에만 사용. **재시도 루프 금지** | 세션 도구가 가장 빠르고 경로 혼선 없음 |
| 4 | **루프 하드캡** — 모든 재시도·검증 순회 **max 2회**. 초과 → 보고 + STOP | 무한 루프 방지 |
| 5 | **원본 유일 = skills-plugin** — 매번 원본에서 새로 가져와야 한다. 반영은 형이 .skill 설치로 직접 수행. **예외: autoloop handoff** — 세션에 `handoff.json`이 존재하면 오토루프 실험장의 최적화된 SKILL.md를 원본으로 사용 | 버전 꼬임 방지. handoff 예외는 오토루프가 이미 최신 검증을 완료했기 때문 |
| 6 | **PREFLIGHT 선행** — 착수 전 **단일 Bash 1회**로 경로·권한·출력경로 3체크. 실패 감지 시 STOP + 보고. 체크 없이 ① 진입 = FAIL | 중간실패 N턴 예방 — EROFS·세션복사본 Read 누락·출력경로 미존재 전부 1턴으로 차단 |

---

## 🚦 PREFLIGHT (착수 전 필수 — 1회 단일 Bash)

**모든 스킬 수정·신규·진단은 이 체크 통과 후에만 ① 진입.**

```bash
# 단일 Bash로 3체크 병렬:
echo "=== ① ORIGIN 경로·권한 ===" && ls -la mnt/.claude/skills/{skill}/SKILL.md 2>&1 | head -5 && \
echo "=== ② SKILL.md 개수 ===" && find mnt/.claude/skills/{skill}/ -name "SKILL.md" | wc -l && \
echo "=== ③ 출력 경로 ===" && ls -d mnt/*/ 2>&1 | grep -v uploads | grep -v .claude
```

| 체크 | 기준 | 실패 시 |
|------|------|---------|
| ① 경로·권한 | ORIGIN SKILL.md 존재·가독 | STOP + 스킬명 확인 요청 |
| ② SKILL.md 1개 | `wc -l` = 1 | STOP (2개+ 시 zip 충돌) |
| ③ 출력 경로 | 마운트 폴더 1개+ 확인 | 스크래치패드 사용으로 전환 |

**Read-before-Edit 의무:** ① 단계에서 세션 복사본을 Cowork Read로 반드시 1회 이상 읽고 Edit 착수. 복사만으로는 불충분 — Cowork 파일추적 상태가 갱신되지 않으면 Edit 실패(`File has not been read yet`).

---

## 실행 흐름 — 선형 3단계

```
🚦 PREFLIGHT → ① 읽기+판정 → [진단이면 보고+종료] → ② 편집 → ②-b 검증+성능게이트 → ③ 패키징+제공
```

### ① 읽기 + 경로 판정

```
ORIGIN = skills-plugin 경로 (mnt/.claude/skills/ 로 접근)
SESSION = /sessions/{session-id}/

0. 핸드오프 감지 (최우선):
   - 세션에 autoloop-lab/{skill-name}/handoff.json 존재?
   - YES → 핸드오프 경로. 아래 1~3 스킵. 오토루프 실험장을 세션 작업본으로 직접 사용.
     **전제: autoloop step 6(볼트 반영) 완료 확인 필수.** handoff.json의 존재만으로는 불충분 — 볼트 원본이 최신인지 diff 확인 후 진행.
     SESSION_SKILL = /sessions/{session-id}/autoloop-lab/{skill-name}/
     handoff.json 읽기 → 점수·변경 요약 확인 → ②-b 검증+성능게이트 → ③ 패키징으로 직행.
     ② 편집은 스킵 (오토루프가 이미 최적화 완료).
   - NO → 기존 경로 (아래 1~4)

1. 원본(ORIGIN)을 세션으로 복사 + 권한 부여:
   Bash: cp -r /sessions/{session-id}/mnt/.claude/skills/{skill}/ /sessions/{session-id}/{skill}/ && chmod -R u+w /sessions/{session-id}/{skill}/
   ⚠ references/, scripts/ 등 하위 폴더도 모두 복사. chmod 필수 — 원본이 read-only이므로 복사본도 read-only로 붙음. 미실행 시 Edit/Write EACCES 에러
2. SKILL.md 읽기 (Cowork Read)
3. python scripts/validate.py (세션에서 실행)
4. 경로 판정 (1회 확정):
   - 진단: "진단해줘/검증해줘" 요청 → validate.py 결과 보고만. ②③ 스킵, 종료. 이후 "수정하자" 시 Skill tool 재발동 필수
   - 경미: 수정 개소 ≤3, 섹션 구조 동일
   - 중간: 섹션 신설·삭제·재배치, 로직 변경
   - 신규: 처음부터 만듦
```

**N개 동시 처리:** 독립 스킬이면 복사 + Read + validate.py를 병렬 tool call로 발행.

### ② 편집

| 경로 | 할 일 | 도구 |
|------|-------|------|
| 경미 | 해당 부분만 수정. description 변경 필요 시 같은 턴에 갱신. **검증: validate.py만. 성능 게이트: 스킵** | Cowork Edit |
| 중간 | 구조 변경 + description 갱신 → ②-b 검증+성능게이트 | Cowork Edit 또는 Write |
| 신규 | 의도→트리거→SKILL.md 작성 → ②-b 검증+성능게이트 | Cowork Write |

**편집 대상 경로:** 세션(`/sessions/{session-id}/{skill}/`). Cowork Edit/Write 사용.

### ②-b 검증 + 성능 게이트 (중간+신규)

편집 완료 후, 패키징 전에 반드시 통과.

**검증 (코드 자동화):**
```bash
cd /sessions/{session-id}
python scripts/validate.py ./{skill}/
# errors=[] → 통과. errors 있으면 수정 후 1회 재실행.
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
# 세션 스크래치패드에서 직접 zip (WORKBENCH 경유 없음)
cd /sessions/{session-id}
rm -f {skill-name}.skill
zip -r {skill-name}.skill {skill-name}/ \
  -x "*.pyc" -x "__pycache__/*" -x ".DS_Store" -x ".git/*" -x "*-workspace/*" -x "evals/*"
```

**출력 경로 — 우선순위:**
1. **스크래치패드 직접 제공** (기본) — `/sessions/{session-id}/{skill-name}.skill`. present_files가 자동으로 outputs 폴더로 복사. mv·cp 불필요.
2. **마운트 폴더 명시 요청 시만** — `cp {skill-name}.skill mnt/{마운트폴더명}/` (PREFLIGHT ③에서 확인한 실존 경로)
3. `mnt/outputs/` 임의 생성 금지 — 해당 경로는 환경 기본값이 아님. 임의 mkdir → present_files INVALID_PATH 오류 유발

```
mcp__cowork__present_files([{"file_path": "/sessions/{session-id}/{skill-name}.skill"}])
```

**네이밍 절대규칙:** .skill 파일명 = 원본 스킬 폴더명 **그대로**. `-1`, `-2`, `_copy` 등 접미사 절대 금지. 형이 명시적으로 네이밍 변경을 지시한 경우만 예외. zip 전 `rm -f {skill-name}.skill`로 기존 파일 선제거 → 중복 회피 접미사 원천 차단.
**재패키징:** outputs에 기존 .skill → 형에게 삭제 확인 → allow_cowork_file_delete → 재패키징.
**git-sync:** 패키징 완료 후 "git push 할까요?" 1줄 제안. 형 컨펌 시 git-sync 발동.

---

## 허브스포크 판정

**전환 절차:** `→ references/hub-spoke-guide.md 참조`
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

## 신규생성 — 스켈레톤 + 트리거 설계

`→ references/new-skill-template.md 참조` (스켈레톤)
`→ references/trigger-guide.md 참조` (트리거)

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
| mnt/.claude/skills/ 직접 쓰기 | 읽기전용. 세션으로 복사 후 편집 → .skill 설치만 반영 |
| `/tmp/` 경로 | Read/Edit 접근 불가. 세션 디렉토리만 사용 |
| **WORKBENCH(`_skills workspace/`) 경유** | **불필요. 세션에서 직접 편집 → zip이 최단 경로. WORKBENCH는 경로 이원화(FS MCP vs Cowork)로 병목 발생** |
| description↔본문 불일치 | description이 발동 판단 유일 입력. 수정 시 동기 확인 |
| zip 대신 tar | .skill은 zip만. tar = 설치 실패 |
| FS MCP 집착 / 순차 처리 | 세션 도구(Read/Write/Edit/Bash) 우선. 독립 스킬은 병렬 tool call |
| SKILL.md 2개 | zip 전 `find {skill}/ -name "SKILL.md" | wc -l`로 1개 확인 |
| 진단→수정 전환 시 발동 누락 | "그럼 수정하자"로 넘어갈 때 **Skill tool 호출 먼저** |
| **EDIT4 직행으로 skill-builder 우회** | SKILL.md가 수정 대상이면 EDIT4 프로토콜 진입 전 skill-builder 발동 필수. "수정해" 요청 → EDIT4 레벨 판정 전에 파일명이 SKILL.md인지 체크 → 맞으면 skill-builder 먼저. 미발동 직접 수정 = FAIL |
| handoff.json 있는데 skills-plugin에서 복사 | 오토루프 최적화 결과를 덮어쓴다. step 0 핸드오프 감지를 반드시 먼저 확인 |
| handoff 경로에서 ② 편집 시도 | 오토루프가 이미 최적화 완료. 편집은 스킵하고 ②-b → ③으로 직행. 추가 수정 필요 시 형에게 확인 |
| **.skill 파일명에 `-1` 등 접미사** | 원본 폴더명 **그대로** 사용. zip 전 `rm -f {skill-name}.skill` 선제거. 형의 명시적 네이밍 변경 지시 없으면 접미사 금지 |
| **"{스킬명} 수정" 패턴 미감지** | P1 "스킬수정"은 일반어. "{디자인스킬/리서치프레임 등} 수정하자"처럼 특정 스킬명+수정 동사 조합도 skill-builder 발동 대상. references/ 하위 파일만 수정해도 .skill 패키징이 필요하므로 skill-builder 경유 필수 |
| **서브에이전트에서 present_files 호출** | Agent tool 내부 세션 경로는 호스트에서 resolve 불가 → `INVALID_PATH`. **③의 zip+cp는 서브에이전트에서 가능하지만, `present_files`는 반드시 부모 세션(메인 대화)에서 호출**. 서브에이전트는 `.skill` 파일 경로만 반환 → 부모가 present |
| **mnt/outputs/ 임의 생성** | 기본 환경에 없음. `mkdir` 후 cp하면 present_files에서 `INVALID_PATH`. 스크래치패드 직접 제공 또는 PREFLIGHT ③에서 확인한 마운트 폴더만 사용 |
| **세션 복사본 Read 누락** | `cp -r` + `chmod`만으론 불충분. Cowork 파일추적 갱신 안 됨 → Edit 호출 시 `File has not been read yet` 오류. 세션 경로로 **Cowork Read 1회 수행 후** Edit 착수 |
| **PREFLIGHT 누락 직행** | 경로·권한·출력경로 미확인 상태로 cp·Edit·zip 진행하면 중간단계 연쇄 실패. 절대규칙 #6 위반 — 착수 전 단일 Bash 1회 필수 |
