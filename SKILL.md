---
name: skill-builder
description: |
  스킬 생성·수정·패키징 **게이트키퍼** — mnt/.claude/skills/ 하위 파일 수정·생성 전 반드시 Skill tool 발동. 미발동=FAIL.
  P1: 스킬, skill, SKILL.md, 스킬수정, 스킬생성, 스킬업데이트, 스킬개선, 트리거수정, description수정, 게이트키퍼, 패키징, 검증.
  P2: 만들어줘, 수정해줘, 수정하자, 고쳐줘, 바꿔줘, 업데이트, 개선, 편집, 손봐, create, fix, refactor, update, modify.
  P3: skill creation, skill modification, skill refactoring.
  P4: SKILL.md·references/·scripts/ 편집, {스킬명}+수정동사 조합, autoloop 완료.
  P5: .skill로.
  NOT: 프롬프트엔지니어링(→직접), 플러그인(→create-cowork-plugin), 최적화루프(→autoloop), UP수정(→up-manager).
vault_dependency: HARD
---

# Skill Builder

스킬 생성·수정·패키징. 선형 흐름 — 분기 최소, 루프 0.

**흐름:** 🚦 PREFLIGHT → ① 읽기+판정 → [진단이면 종료] → ② 편집 → ②-b 검증+성능게이트 → ③ 패키징+제공

---

## ⛔ 절대 규칙 (6개)

| # | 규칙 | 이유 |
|---|------|------|
| 1 | **게이트키퍼** — `mnt/.claude/skills/` 하위 **어떤 파일이든**(SKILL.md·references/·scripts/·assets/) 수정·생성·삭제·이름변경 전 **반드시 `Skill tool`로 skill-builder 발동**. 도구 무관(Edit/Write/Bash mv/Bash rm). **감지:** ①경로가 `mnt/.claude/skills/` 하위 ②대화에 스킬명+수정동사 ③"스킬 수정/고쳐/바꿔/업데이트" 언급 ④진단→수정 전환 ⑤EDIT4 직행 — 하나라도 걸리면 Skill tool 호출 먼저 | description이 발동 판단 유일 입력. 미발동 = 버전 꼬임·검증 누락 |
| 2 | **수정 완료 = .skill 패키징 제공** | 사용자가 설치할 수 없음 |
| 3 | **세션 내 직접 편집** — 원본→세션 복사 → Cowork Edit/Write → zip → present. FS MCP는 plugin_skills_path 반영 시에만 | 세션 도구가 최단 경로. WORKBENCH 경유 = 이원화 병목 |
| 4 | **루프 하드캡** — 재시도·검증 순회 **max 2회**. 초과 → 보고 + STOP | 무한 루프 방지 |
| 5 | **원본 유일 = skills-plugin** — 매번 원본에서 새로. **예외: autoloop handoff** — 세션에 `handoff.json` 존재 시 오토루프 실험장을 원본으로 사용 | 버전 꼬임 방지. handoff는 오토루프 검증 완료 상태 |
| 6 | **PREFLIGHT 선행** — 착수 전 단일 Bash 1회로 경로·권한·출력경로 3체크 + 세션 복사본 Read 1회. 미수행 시 ① 진입 = FAIL | EROFS·Read 누락·출력경로 미존재 연쇄 실패 1턴 차단 |

---

## 🚦 PREFLIGHT (단일 Bash 1회)

```bash
echo "=== ① ORIGIN 경로·권한 ===" && ls -la mnt/.claude/skills/{skill}/SKILL.md 2>&1 | head -5 && \
echo "=== ② SKILL.md 개수 ===" && find mnt/.claude/skills/{skill}/ -name "SKILL.md" | wc -l && \
echo "=== ③ 출력 경로 ===" && ls -d mnt/*/ 2>&1 | grep -v uploads | grep -v .claude
```

| 체크 | 기준 | 실패 시 |
|------|------|---------|
| ① 경로·권한 | ORIGIN SKILL.md 존재·가독 | STOP + 스킬명 확인 요청 |
| ② SKILL.md 1개 | `wc -l` = 1 | STOP (2개+ 시 zip 충돌) |
| ③ 출력 경로 | 마운트 폴더 1개+ | 스크래치패드로 전환 |

**Read-before-Edit 의무:** 세션 복사본을 Cowork Read로 1회 이상 읽고 Edit 착수. `cp + chmod`만으론 Cowork 파일추적 갱신 안 됨 → `File has not been read yet` 에러.

---

## ① 읽기 + 경로 판정

**0. 핸드오프 감지 (최우선):** 세션에 `autoloop-lab/{skill-name}/handoff.json` 존재?
- **YES** → 1~3 스킵. `SESSION_SKILL = /sessions/{session-id}/autoloop-lab/{skill-name}/` 사용. handoff.json 점수 확인 → ②-b → ③ 직행. ② 편집은 스킵(오토루프가 이미 최적화). **전제: autoloop step 6(볼트 반영) 완료 확인** — diff로 원본 최신성 확인 후 진행.
- **NO** → 아래 1~4.

**1. 원본→세션 복사 + 권한:**
```bash
cp -r /sessions/{session-id}/mnt/.claude/skills/{skill}/ /sessions/{session-id}/{skill}/ && \
chmod -R u+w /sessions/{session-id}/{skill}/
```
references/, scripts/ 등 하위폴더 모두. chmod 필수(원본 read-only → 복사본도 read-only).

**2. SKILL.md 읽기** (Cowork Read)
**3. `python scripts/validate.py ./{skill}/`** 세션에서 실행
**4. 경로 판정 (1회 확정):**

| 경로 | 조건 | 다음 단계 |
|------|------|----------|
| 진단 | "진단해줘/검증해줘" 요청 | validate 결과 보고 → 종료. 이후 스킬수정 시 Skill tool 재발동 |
| 경미 | 수정 개소 ≤3, 구조 동일 (트리거수정·description수정 등 국소 스킬업데이트) | ② 경미 |
| 중간 | 섹션 신설·삭제·재배치, 로직 변경 (스킬개선) | ② 중간 |
| 신규 | 처음부터 (스킬생성) | ② 신규 → `→ references/new-skill-template.md 참조` |

**N개 동시 처리:** 독립 스킬이면 복사+Read+validate를 병렬 tool call.

---

## ② 편집

| 경로 | 할 일 | 도구 | 다음 |
|------|-------|------|------|
| 경미 | 해당 부분만 수정. description 변경 필요 시 같은 턴에 갱신 | Cowork Edit | validate.py만. 성능게이트 스킵 → ③ |
| 중간 | 구조 변경 + description 갱신 | Cowork Edit/Write | ②-b |
| 신규 | 의도→트리거→작성. `→ references/new-skill-template.md`, `→ references/trigger-guide.md` | Cowork Write | ②-b |

편집 대상: 세션(`/sessions/{session-id}/{skill}/`).

---

## ②-b 검증 + 성능 게이트 (중간·신규)

**검증:**
```bash
cd /sessions/{session-id} && python scripts/validate.py ./{skill}/
# errors=[] → 통과. errors 있으면 수정 후 1회 재실행. 2회차 실패 → STOP + 보고
```

**성능 게이트:** `→ references/perf-checklist.md 참조` (실행 속도 저하 7대 원인·트레이드오프 금지선 포함)

| # | 체크 | 자동화 | 수정 포인터 |
|---|------|--------|-----------|
| 1 | 허브스포크 (허브=분기·규칙·포인터만) | validate.py → `hub_spoke` | `→ references/hub-spoke-guide.md` |
| 2 | 불필요 로딩 방지 | @uses vs 본문 포인터 비교 | `→ references/perf-checklist.md §로딩` |
| 3 | 코드 대체 가능성 | validate.py → `automatable_sections` | `→ references/perf-checklist.md §코드화` |
| 4 | 토큰 예산 | validate.py → `combined_tokens_estimate` (>30K 경고) | 스포크 추가 분리 |
| 5 | 병목 구간 | validate.py → `phases_count` + 텍스트 비중 | 섹션 통합·압축 |

---

## ③ 패키징 + 제공

```bash
cd /sessions/{session-id}
rm -f {skill-name}.skill    # 기존 제거 → 접미사(-1, _copy) 원천 차단
zip -r {skill-name}.skill {skill-name}/ \
  -x "*.pyc" -x "__pycache__/*" -x ".DS_Store" -x ".git/*" -x "*-workspace/*" -x "evals/*"
```

**출력 경로 우선순위:**
1. **스크래치패드 직접 제공 (기본)** — `/sessions/{session-id}/{skill-name}.skill`. present_files가 outputs 폴더로 자동 복사. mv·cp 불필요.
2. **마운트 폴더 명시 요청 시만** — `cp {skill-name}.skill mnt/{마운트폴더명}/` (PREFLIGHT ③에서 확인한 실존 경로)
3. **`mnt/outputs/` 임의 생성 금지** — 환경 기본값 아님. 임의 mkdir → present_files INVALID_PATH

```
mcp__cowork__present_files([{"file_path": "/sessions/{session-id}/{skill-name}.skill"}])
```

**네이밍:** .skill 파일명 = 원본 폴더명 **그대로**. `-1`·`_copy` 접미사 금지(형의 명시적 지시 시만 예외).
**재패키징:** 기존 .skill → 형 컨펌 → `allow_cowork_file_delete` → 재zip.
**서브에이전트:** zip+cp는 가능. `present_files`는 반드시 부모 세션(메인 대화)에서 호출.
**git-sync:** 패키징 완료 후 "git push 할까요?" 1줄 제안. 형 컨펌 시 git-sync 발동.

---

## 신규생성 요약

허브스포크: `→ references/hub-spoke-guide.md`
스켈레톤: `→ references/new-skill-template.md`
트리거: `→ references/trigger-guide.md`

**트리거 티어 (최소):** P1 5+ / P2 2(한+영) / P3 2+ / P4 0-2 / P5 1+ / NOT 필수
**Lean 기준:** SKILL.md 목표 5KB·최대 10KB / 표 우선 / 결정적 작업은 scripts/ / "왜" 필수 / 예시 1+ / Gotchas 필수
**description은 적극적으로** — Claude는 스킬을 덜 쓰는 쪽으로 편향. 범위를 넓혀라.

```
skill-name/
├── SKILL.md          (필수)
├── references/       (필요시 로딩)
├── scripts/          (결정적·반복적 작업 코드화)
└── assets/           (출력용)
```

---

## 배치 모드

2개+ 스킬 동시 요청 시: 같은 단계끼리 묶어 병렬 발행.
```
Read(A)+Read(B) → Edit(A)+Edit(B) → zip A & zip B & wait → present_files
```

---

## Gotchas (외부 함정 전용 — 본문 규칙 복제 금지)

| 함정 | 대응 |
|------|------|
| `mnt/.claude/skills/` 직접 쓰기 | 읽기전용. 세션 복사 후 편집 → .skill 설치로만 반영 |
| `/tmp/` 경로 | Read/Edit 접근 불가. 세션 디렉토리만 |
| WORKBENCH(`_skills workspace/`) 경유 | 불필요. FS MCP vs Cowork 경로 이원화로 병목 |
| description↔본문 불일치 | description이 발동 판단 유일 입력. 수정 시 본문 동기 확인 |
| zip 대신 tar | .skill은 zip만. tar = 설치 실패 |
| FS MCP 집착·순차 처리 | 세션 도구(Read/Write/Edit/Bash) 우선. 독립 스킬은 병렬 tool call |
| SKILL.md 2개 | zip 전 `find {skill}/ -name "SKILL.md" \| wc -l`로 1 확인 |
| handoff.json 있는데 skills-plugin 복사 | 오토루프 최적화 결과 덮어씀. ①.0 핸드오프 감지 먼저 |
