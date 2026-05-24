---
name: skill-builder
description: 스킬 생성·수정·패키징·검증 1턴 완결 게이트키퍼. v3.1 9룰 베놈 — Prereq·NextPhase·OutputPath·RefIndex·Boundaries·WhenToUse·FailureModes 강제 + metadata 표준화. mnt/.claude/skills 편집 직전 강제 발동. P1 스킬빌더, skill builder, skill creator, SKILL.md, 스킬생성, 스킬수정, 스킬패키징, 스킬검증, 트리거수정, 게이트키퍼, 9룰베놈. P2 만들어줘, 수정해줘, 고쳐줘, 바꿔줘, create, fix, update. P3 skill creation, skill modification, skill packaging, 9-rule discipline. P4 SKILL.md·references·scripts 편집·{스킬명}+수정동사·autoloop 완료. P5 .skill로. NOT 프롬프트엔지니어링(→직접), 플러그인(→cowork-plugin-management:create-cowork-plugin), 최적화루프(→autoloop), UP수정(→up-manager).
metadata:
  author: jason
  version: "3.1.0"
---

# skill-builder v3.2

**1턴 완결.** ① 복사 → ② 묶음편집·검증 → ③ Dry-run → ④ 패키징·Host sync.

**v3.2 안티-뱅뱅 (2026-05-24):** v3.1 베놈 위에 4대 RCA 패치 — ① heredoc 실패 진단 표준 ② host/VM 경로 진실 매핑 ③ 성능 패치 시 캐시 무효화 강제 ④ sync 스크립트 환경 의존 명시. 상세 → `references/anti-bangbang.md`.

**v3.1 베놈:** 모든 신규·수정 스킬에 **9룰 강제 적용**. SKILL.md 골격에 Prereq·NextPhase·OutputPath·RefIndex·Boundaries·WhenToUse·FailureModes 7섹션 강제 + metadata 표준화 + description 첫문장 평문화 권고.

## Skill Boundaries

- **하는 것** — SKILL.md 편집·references/scripts 갱신·9룰 강제 적용·검증·패키징·host sync
- **안 하는 것** — 스킬 품질 진단(→ skill-doctor) · 자동변이/최적화(→ autoloop) · 플러그인 패키징(→ create-cowork-plugin) · UP 편집(→ up-manager)

## When to Use

- 사용자가 "{스킬명} 수정해줘·고쳐줘·바꿔줘" — 단일 스킬 편집
- 신규 스킬 생성 요청 ("X 스킬 만들어줘")
- autoloop 루프 종료 후 handoff.json 감지 — 자동 패키징 모드
- skill-doctor 처방전 수신 — 처방대로 수정 후 패키징
- **안 쓸 때** — 단순 질문, 스킬 진단만 원함(→ skill-doctor), 자동 최적화(→ autoloop)

## Prerequisites

본 스킬 진입 전 다음을 체크. 미충족 시 STOP + 안내.

| # | 체크 | 미충족 시 |
|---|------|-----------|
| 1 | `mnt/.claude/skills/{SKILL}/` 존재 (수정 모드) | "스킬명 오타? 또는 신규 생성 모드인가요?" 질문 |
| 2 | SESSION_ID 추출 (system prompt) | system prompt의 `/sessions/{id}/mnt/` 경로 grep |
| 3 | 9룰 적용 의도 확인 (신규 스킬) | 9룰 골격 자동 삽입. 수정 모드는 누락 룰만 보강 |
| 4 | autoloop handoff.json 있나? (선택) | 있으면 ① 복사 단계 스킵, 핸드오프 사용 |

## ⛔ 절대 규칙 (5)

| # | 규칙 |
|---|------|
| 1 | **게이트키퍼** — `mnt/.claude/skills/` 편집 전 본 스킬 발동. 미발동 = FAIL |
| 2 | **수정 완료 = `mnt/outputs/{skill}.skill` 1개 + host plugin path rsync** |
| 3 | **편집은 VM `/sessions/$SESSION_ID/$SKILL/`** — host 원본 read-only |
| 4 | **루프 max 2회** — 검증 실패 1회 재시도, 2회차 = STOP |
| 5 | **9룰 베놈 강제** — 신규 스킬은 7섹션(Boundaries·WhenToUse·Prereq·OutputPath·RefIndex·NextPhase·FailureModes) 골격 자동 삽입. 수정 모드는 누락 룰 보강. 미적용 = FAIL |
| 6 | **안티-뱅뱅 (v3.2)** — heredoc 안 `applied/skipped` 리스트 + `AssertionError` 메시지에 실패 패치 태그·snippet 강제. host경로는 `mnt/outputs/` 경유. 성능 패치는 캐시 rm 후 측정. sync는 git-sync 스킬 위임 |

## ① 복사

**세션 ID = system prompt에서 직접 추출** (`ls /sessions/` ✗ — 권한 거부됨).

```bash
SESSION_ID=sleepy-charming-cray  # system prompt에서 추출
SKILL=skill-name

rm -rf /sessions/$SESSION_ID/$SKILL && \
mkdir -p /sessions/$SESSION_ID/$SKILL && \
cp -r /sessions/$SESSION_ID/mnt/.claude/skills/$SKILL/* /sessions/$SESSION_ID/$SKILL/ && \
chmod -R u+w /sessions/$SESSION_ID/$SKILL/ && \
wc -l /sessions/$SESSION_ID/$SKILL/SKILL.md
```

**경로 판정 1줄:** 진단(검증해줘) / 경미(≤3곳) / 중간(섹션 신설) / 신규(처음부터) / 리팩토링(분량·구조 재설계) / **베놈(9룰 누락 보강)**.

## ② 묶음 편집·검증 (1회 heredoc)

**원칙: 편집·assert·len()·9룰 grep을 단일 heredoc에 묶는다.**

```bash
cd /sessions/$SESSION_ID && python3 << 'EOF'
import re
p = "skill-name/SKILL.md"
s = open(p).read()

# 편집
edits = [("OLD 1", "NEW 1"), ("OLD 2", "NEW 2")]
for o, n in edits:
    assert o in s, f"missing: {o[:40]}"
    s = s.replace(o, n, 1)
open(p, "w").write(s)

# description ≤1024 검증
m = re.search(r"^description:\s*(.+?)(?=^\w+:|\Z)", s, re.MULTILINE|re.DOTALL)
desc_len = len(m.group(1).strip()) if m else 0
assert desc_len <= 1024, f"description {desc_len}/1024 초과"

# 9룰 베놈 grep — 7섹션 존재 확인
required = ["Skill Boundaries", "When to Use", "Prerequisites", "Output", "Reference Index|references/", "Next Phase|→ ", "Failure Modes|Gotchas"]
missing = [r for r in required if not re.search(r, s)]
assert not missing, f"9룰 누락: {missing}"

# v3.2 안티-뱅뱅: applied/skipped 리스트 강제 (진단 콜 0회)
print(f"applied={[o[:30] for o,_ in edits]} desc={desc_len}/1024 9rules=OK")
EOF
```

**v3.2 진단 출력 룰 (필수):**
- 편집 루프 안 `if old in s` 가드 → 실패 시 `raise AssertionError(f"FAILED at: {tag}")` (어느 패치 단계인지 즉시 식별)
- heredoc 끝 `print(f"applied={[...]} skipped={[...]} len={len(s)}")` 강제
- 효과: 형이 "뭐 들어갔어/안 들어갔어?" 진단 콜 0회. 상세 → `references/anti-bangbang.md`.

**전면 재작성:** 단일 `python3` heredoc 안에서 `open(p,"w").write(new_content)` + 동일 heredoc에 검증.

상세 — `→ references/edit-protocol.md`.

## ③ Dry-run 시뮬레이션 (패키징 직전 강제)

```bash
python3 /sessions/$SESSION_ID/skill-builder/scripts/dry_run.py /sessions/$SESSION_ID/$SKILL/
```

**검증:** validate.py errors=[] **AND** dry_run.py PASS **AND** 9룰 7섹션 grep PASS 동시 충족.

```bash
cd /sessions/$SESSION_ID && \
python3 skill-builder/scripts/validate.py ./$SKILL/ | grep -E '"valid"|"errors"' && \
python3 skill-builder/scripts/dry_run.py ./$SKILL/
```

**컨펌 1줄 (패키징 직전):** `경로: {경미/중간/신규/베놈/리팩토링} · 변경 N · validate=OK · dry-run=PASS · 9룰=OK → 진행할까?` 형이 "끝까지·전부·일괄·리팩토링" 명시 시 Skip.

## ④ 패키징 + Host sync

```bash
SESSION_ID=magical-festive-keller; SKILL=skill-name
cd /sessions/$SESSION_ID && \
rm -f $SKILL.skill && \
zip -qr $SKILL.skill $SKILL/ -x "*.pyc" "__pycache__/*" ".DS_Store" "evals/*" && \
cp $SKILL.skill mnt/outputs/$SKILL.skill && \
ls -la mnt/outputs/$SKILL.skill
```

**Host sync 정책 (v3.2 명시):**
- `sync-to-host-plugin.sh`는 **host shell 전용·git-sync env 의존**. VM bash에서 호출 ✗
- skill-builder ④ = `mnt/outputs/{SKILL}.skill` 출고만 강제. host plugin 동기는 git-sync 스킬에 위임
- 형이 명시 요청 시에만 git-sync 호출

### v3.2 경로 진실 매핑 (뱅뱅이 차단 핵심)

| 경로 | VM bash(workspace) | host bash(DC) |
|---|---|---|
| `/sessions/{id}/...` | ✅ R/W | ❌ |
| `/Users/jason/...` | ❌ | ✅ R/W |
| `mnt/outputs/` ↔ `~/Library/.../local_*/outputs/` | 양쪽 동일 | 양쪽 동일 |
| `mnt/.claude/skills/{X}/` | Read-only | ❌ |
| `~/github-repos/.../scripts/` | ❌ | ✅ R/W |

**VM→Host 파일 전달 패턴:**
1. VM bash: `cp /sessions/.../patched mnt/outputs/`
2. DC bash: `cp "$HOST_OUTPUTS/patched" ~/github-repos/.../target`

DC outputs 절대경로:
```bash
OUT=$(ls -td "$HOME/Library/Application Support/Claude/local-agent-mode-sessions"/*/*/local_*/outputs | head -1)
```

**제공:** `[다운로드](computer://...)` 1줄. **git push 제안:** 옵션·답 없으면 ✗.

## Output Path (산출물 경로 명시)

| 산출물 | 경로 | 비고 |
|---|---|---|
| .skill 패키지 | `mnt/outputs/{SKILL}.skill` | 형이 다운로드하는 정본 |
| host plugin sync | host plugin path | git-sync가 보는 위치 |
| 리서치 결과 | `{VAULT}/_skills research/{SKILL}/{YYYY-MM-DD}_{topic}.md` | 세션 종료 시 소실 방지 |
| handoff (autoloop 연계) | `/sessions/{id}/autoloop-lab/{SKILL}/handoff.json` | 패키징 input |

## Reference Index

references/ 폴더의 어떤 파일을 언제 읽는지.

| 파일 | 내용 | 언제 |
|---|---|---|
| `references/edit-protocol.md` | 묶음 편집 heredoc 패턴 | ② 편집 시 |
| `references/new-skill-template.md` | 신규 스킬 골격 (9룰 포함) | 신규 생성 시 |
| `references/trigger-guide.md` | description 트리거 작성법 (P1~NOT) | description 작성·수정 시 |
| `references/9-rules-template.md` | 7섹션 골격 스니펫 | 베놈 모드 (9룰 보강) |
| `references/anti-bangbang.md` | 뱅뱅이 4대 RCA + 진단 출력 패턴 (v3.2) | 묶음 heredoc 작성·성능 패치·VM↔Host 전달 시 |

## 신규생성 (9룰 베놈 골격 자동 삽입)

```
skill-name/
├── SKILL.md          (≤500줄·목표 200~300·9룰 7섹션 강제)
├── references/       (도메인 지식 ≥1개)
├── scripts/          (결정적·반복 작업)
└── assets/           (출력 템플릿)
```

**SKILL.md 7섹션 강제 골격:**
1. `## Skill Boundaries` — 하는 것/안 하는 것
2. `## When to Use` — 상황 묘사 2~5줄 (P2 동사 + 시나리오)
3. `## Prerequisites` — 시작 전 체크 표
4. `## ⛔ 절대 규칙` — 5~7개 표
5. `## Output Path` — 산출물 경로 결정론
6. `## Reference Index` — references/ 폴더 표
7. `## Next Phase` + `## Failure Modes (Gotchas)` — 다음 스킬 추천 + 흔히 망치는 패턴

description ≤1024자·3인칭/명령형·**첫 문장은 평문 한 문장** (외부 LLM 호환). 표 우선·"왜" 필수·예시 1+·Gotchas 필수.

상세 — `→ references/new-skill-template.md`, `→ references/trigger-guide.md`, `→ references/9-rules-template.md`.

## 배치 (N개 동시)

```bash
cd /sessions/$SESSION_ID && python3 << 'EOF'
edits = {"skill-A": [("o1","n1")], "skill-B": [("oX","nY")]}
for skill, pairs in edits.items():
    p = f"{skill}/SKILL.md"; s = open(p).read()
    for o, n in pairs:
        assert o in s; s = s.replace(o, n, 1)
    open(p, "w").write(s)
EOF
for sk in skill-A skill-B; do
  (cd /sessions/$SESSION_ID && zip -qr "$sk.skill" "$sk/" -x "*.pyc" ".DS_Store") &
done; wait
```

## Next Phase

본 스킬 작업 후 자연스럽게 이어지는 흐름:

- **검증·진단** → `skill-doctor` (32셀 매트릭스로 수정 후 건강도 측정)
- **자동 최적화** → `autoloop` (eval 기반 변이 루프로 점수 상승)
- **레포 동기화** → `git-sync` (host plugin sync 후 GitHub push)
- **세션 마무리** → `session-briefing` (작업 결정·미결·다음을 VAULT 저장)

## Failure Modes (Gotchas)

| 함정 | 대응 |
|---|---|
| 매 step `head·grep·ls` 재확인 | **v2.0 실패 본질.** 묶음 heredoc 1회로 편집·assert·len()·검증 통합 |
| VM 편집 후 git-sync "변경 없음" | host plugin path 미동기. ④의 `sync-to-host-plugin.sh` 강제 |
| description 1024 초과 사후 적발 | 편집 heredoc 안 `len()` assert 즉시 측정 |
| `ls /sessions/` 1000개 출력 | 권한 거부. system prompt의 SESSION_ID 직추출 |
| 패키징 = 끝 보고 | 실제 발동 시 작동 안 할 수 있음. `dry_run.py` PASS 필수 |
| `mnt/.claude/skills/` 직접 쓰기 | read-only. VM 복사 후 편집 |
| `cp+chmod`만 하고 Read 안 함 | Cowork 파일추적 미갱신. Read 1회 필수 |
| `.skill` 접미사 `-1`·`_copy` | 마운트 구파일 미삭제. ④에서 `rm -f` 선행 |
| zip 대신 tar | .skill = zip 전용 |
| autoloop handoff 무시 | `autoloop-lab/$SKILL/handoff.json` 감지 시 ① 스킵·핸드오프 사용 |
| 리서치 outputs 저장 | 세션 종료 = 소실. VAULT만 |
| description ↔ 본문 불일치 | description = 발동 판단 유일 입력 |
| **9룰 7섹션 누락한 채 패키징** | 절대규칙 5 위반. 7섹션 grep PASS 후 진행 |
| **신규 스킬에 Boundaries·WhenToUse 누락** | 트리거 충돌 시 디스앰비게이트 불가. 골격 강제 삽입 |
| **Prerequisites 누락한 채 시작** | 의존 파일 없을 때 침묵 실패. 본문 상단에 체크 표 |
| **(v3.2) 묶음 heredoc 실패 시 진단 콜 폭증** | assert에 실패 태그·snippet 강제. heredoc 끝 `applied/skipped` 출력 강제. 형 진단 콜 0회 |
| **(v3.2) VM↔Host 경로 혼동으로 cp 실패** | §④ 경로 진실 매핑 표 참조. VM `/sessions/`는 DC에서 ✗. host `/Users/`는 VM에서 ✗. `mnt/outputs/` ↔ `~/Library/.../outputs/`만 양쪽 동일 |
| **(v3.2) 성능 패치 dry-run PASS인데 실측 0초 컷** | 대상 스크립트에 sha256·캐시 short-circuit이 있으면 `.cache/` rm 후 재측정 강제 |
| **(v3.2) sync-to-host-plugin.sh를 VM에서 호출** | host shell·git-sync env 전용. VM에서 호출 = 부재 exit. ④에서 호출 ✗. git-sync 스킬이 별도 사용 |
| **(v3.2) 디스크 풀로 파일 truncated** | `df -h /sessions` 확인. 부족 시 `/sessions/$SID/{skill명}` 작업본·`.skill` zip 정리. 작성 직후 `wc -c` 검증 |

## ❌ WRONG vs ✅ CORRECT

```
❌ WRONG: 신규 스킬 생성 시 frontmatter + 본문 1섹션만 작성 (9룰 누락)
✅ CORRECT: 7섹션 골격(Boundaries·WhenToUse·Prereq·OutputPath·RefIndex·NextPhase·FailureModes) 자동 삽입 후 도메인 내용 채움
```

```
❌ WRONG: 수정 후 패키징만 하고 host plugin sync 누락 → git-sync "변경 없음"
✅ CORRECT: 형 명시 요청 시 git-sync 스킬 별도 호출 (skill-builder ④는 outputs 출고만)
```

```
❌ WRONG (v3.2 안티-뱅뱅): 묶음 heredoc 실패 후 "어디까지 들어갔지?" 진단 콜 3회 (sed/grep/find 따로)
✅ CORRECT: assert에 실패 태그 + heredoc 끝 `applied/skipped` 출력 → 1콜로 진단 완료
```

```
❌ WRONG: 성능 패치 후 dry-run PASS만 보고 출고 → 실측 sha256 short-circuit으로 0초 컷
✅ CORRECT: 캐시 식별 → `rm .cache/...` → 실측 → before/after 시간 명시
```

```
❌ WRONG: VM에서 `cp /sessions/... ~/github-repos/...` → "No such file"
✅ CORRECT: VM `cp /sessions/... mnt/outputs/...` → DC `cp "$OUT/..." ~/github-repos/...`
```
