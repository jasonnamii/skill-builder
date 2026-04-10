---
name: skill-builder
description: |
  스킬 생성·수정·패키징 유일한 게이트키퍼. SKILL.md 파일을 write_file·edit_file·Write·Edit 등 어떤 도구로든 수정하기 전에, 반드시 Skill tool로 skill-builder를 먼저 발동해야 함. 발동 없이 직접 수정 = FAIL. 스킬 진단·분석·리팩터링·재작성·트리거 설계·Lean 작성·검증·.skill 패키징까지 전 과정 수행. 스킬 파일을 건드리는 모든 작업에서 발동.
  P1: 스킬, skill, SKILL.md, 패키징, 검증, 스킬만들기, 스킬수정, 스킬고치기, 스킬리팩터링.
  P2: 만들어줘, 수정해줘, 고쳐줘, 재작성해줘, validate, create, fix, refactor.
  P3: skill creation, skill modification, skill refactoring, description optimization.
  P4: SKILL.md를 편집하려 할 때, 스킬 파일을 write_file·edit_file로 쓰려 할 때, 스킬 구조를 변경하려 할 때.
  P5: .skill로.
  NOT: 프롬프트엔지니어링(→직접), 플러그인(→create-cowork-plugin), 스킬최적화루프(→autoloop), 다른 스킬 단순 사용(→해당 스킬).
---

# Skill Builder

스킬 생성·수정·패키징. 선형 흐름 — 분기 최소, 루프 0.

---

## ⛔ 절대 규칙 (4개만)

| # | 규칙 | 이유 |
|---|------|------|
| 1 | **게이트키퍼** — SKILL.md를 수정·생성·재작성하기 전에 **반드시 `Skill tool`로 skill-builder를 먼저 발동**. FS write_file/edit_file이든 Cowork Write/Edit이든 **도구 무관 — 발동이 먼저**. 미발동 상태에서 스킬 파일 수정 착수 = FAIL. 진단·분석 후 수정으로 이어지는 경우에도 수정 직전에 반드시 발동 | 스킬 '사용'≠'수정'. "분석해줘"=무관. 진단 후 수정 전환 시 발동 누락이 가장 흔한 위반 |
| 2 | **수정 완료 = .skill 패키징 제공** — 패키징 없이 끝내면 미완료 | 사용자가 설치할 수 없음 |
| 3 | **Cowork Read/Edit 기본** — 세션 디렉토리에 복사 후 편집. FS MCP는 선택사항(가능하면 사용, 불가 시 Cowork로 진행). **FS 불가를 이유로 멈추거나 재시도 루프 금지** | FS 강제가 ToolSearch→실패→재시도 뺑뺑이의 근본 원인 |
| 4 | **루프 하드캡** — 모든 재시도·검증 순회는 **max 2회**. 초과 시 현재 상태 보고 + STOP. 자동 복구 시도 금지 | 무한 루프 방지 |

---

## 실행 흐름 — 선형 3단계

모든 경로가 이 3단계를 따른다. 분기는 단계 내부에서만.

```
① 읽기+판정 → ② 편집 → ③ 패키징+제공
```

### ① 읽기 + 경로 판정

```
1. mnt/.claude/skills/{skill}/ 전체를 세션 디렉토리로 복사
   cp -r mnt/.claude/skills/{skill} ./{skill}/ && chmod -R u+w ./{skill}/
2. SKILL.md 읽기 (Read tool)
3. 경로 판정 (1회 확정, 변경 불가):
   - 경미: 수정 개소 ≤3, 섹션 구조 동일
   - 중간: 섹션 신설·삭제·재배치, 로직 변경
   - 신규: 처음부터 만듦
```

**N개 동시 처리:** 독립 스킬이면 cp + Read를 병렬 tool call로 발행.

### ② 편집

| 경로 | 할 일 | 도구 |
|------|-------|------|
| 경미 | 해당 부분만 수정. description 변경 필요 시 같은 턴에 갱신 | Edit (부분 교체) |
| 중간 | 구조 변경 + description 갱신 + 검증 체크리스트 1회 | Edit 또는 Write (전면 재작성 시) |
| 신규 | 의도→트리거→SKILL.md 작성 + 검증 체크리스트 1회 | Write |

**Edit vs Write 판단:** 부분 수정 = Edit (나머지 보존). 전면 재작성/신규 = Write.

**검증 체크리스트 (중간+신규만, 1회 실행):**
- YAML frontmatter `---`로 시작/종료
- name: lowercase+hyphens, 64자 이내
- description: 500자 이내, YAML에 탭 없음
- P1 5개+, P2 2개+, P3 2개+, P5 1개+, NOT 존재
- SKILL.md ≤ 10KB
- 실패 항목 → 즉시 수정 (같은 턴). **2회차 검증 실패 → STOP + 보고**

### ③ 패키징 + 제공

```bash
# 기존 .skill 제거 → zip → present_files
rm -f /sessions/{session-id}/{skill-name}.skill
cd /sessions/{session-id}/mnt/.claude/skills
zip -r /sessions/{session-id}/{skill-name}.skill {skill-name}/ \
  -x "*.pyc" -x "__pycache__/*" -x ".DS_Store" -x ".git/*" -x "*-workspace/*" -x "evals/*"
```

```
mcp__cowork__present_files([{"file_path": "/sessions/{session-id}/{skill-name}.skill"}])
```

**재패키징:** outputs에 기존 .skill 있으면 → 형에게 삭제 확인 → allow_cowork_file_delete → 재패키징.

**git-sync:** 패키징 완료 후 "git push 할까요?" 1줄 제안. 형 컨펌 시 git-sync 발동. 거절 시 스킵.

---

## 허브스포크 판정

**판정 시점:** ① 읽기 단계에서 1회만. 전환도 1회만 — 전환 후 재판정 금지.

| 조건 (하나라도) | 결과 |
|----------------|------|
| SKILL.md >5KB 예상 | 허브스포크 |
| 독립 참조 블록 2개+ | 허브스포크 |
| 단일인데 10KB 근접 또는 섹션 6개+ | 허브스포크 전환 |
| 해당 없음 | 단일 유지 |

**허브:** 분기·규칙·포인터만. 목표 3KB, 최대 5KB. 세부는 `references/`로 분리.
**스포크:** 경로별 절차, 스키마, 도메인 지식 등 필요 시에만 로딩.
**포인터:** `→ references/{파일명}.md 참조`

---

## 신규생성 — 트리거 설계

`references/trigger-guide.md` 참조.

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
| 코드 최소 | 패턴만, 20줄 이내 |
| 중복 제거 | 같은 내용 1회만 |
| "왜" 필수 | 이유 없는 지시 → LLM이 무시함 |
| 예시 1개+ | 없으면 출력 자의적 |
| Gotchas 필수 | 실패 패턴 명시 |

```
스킬 구조:
skill-name/
├── SKILL.md          (필수)
├── references/       (필요시 로딩)
├── scripts/          (결정적 작업)
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
| mnt/.claude/skills/ 직접 쓰기 | 읽기전용. 세션 복사 후 편집 → .skill 패키지 설치만 반영 |
| `/tmp/` 경로 | Read/Edit 접근 불가. 세션 디렉토리만 사용 |
| description↔본문 불일치 | description이 발동 판단 유일 입력. 수정 시 동기 확인 |
| zip 대신 tar | .skill은 zip만. tar 사용 시 설치 실패 |
| 순차 처리 | 독립 스킬은 병렬 tool call. 순차 = 턴 N배 낭비 |
| SKILL.md 2개 | zip 전 `find {skill}/ -name "SKILL.md" \| wc -l`로 1개 확인 |
| FS MCP 집착 | FS 불가 시 Cowork로 즉시 진행. 재시도 루프 금지 |
| 검증 뺑뺑이 | 체크리스트 2회 초과 → STOP. 자동 복구 금지 |
| 진단→수정 전환 시 발동 누락 | 스킬 진단·분석 후 "그럼 수정하자"로 넘어갈 때 skill-builder 발동 안 하고 직접 FS/Edit으로 파일 수정하는 패턴. **수정 착수 전 반드시 Skill tool 호출** |
