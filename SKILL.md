---
name: skill-builder
description: 스킬 생성·수정·패키징·검증 1턴 완결 게이트키퍼. v3.0 묶음검증·VM↔Host 자동 sync·Dry-run 시뮬·description 사전측정. mnt/.claude/skills 편집 직전 강제 발동. P1 스킬빌더, skill builder, skill creator, SKILL.md, 스킬생성, 스킬수정, 스킬패키징, 스킬검증, 트리거수정, 게이트키퍼. P2 만들어줘, 수정해줘, 고쳐줘, 바꿔줘, create, fix, update. P3 skill creation, skill modification, skill packaging. P4 SKILL.md·references·scripts 편집·{스킬명}+수정동사·autoloop 완료. P5 .skill로. NOT 프롬프트엔지니어링(→직접), 플러그인(→create-cowork-plugin), 최적화루프(→autoloop), UP수정(→up-manager).
---

# skill-builder v3.0

**1턴 완결.** ① 복사 → ② 묶음편집·검증 → ③ Dry-run → ④ 패키징·Host sync.

**v3.0 본질 5:** 매 step 검증 ✗·묶음 1회 ○ / VM↔Host 자동 rsync / Dry-run 시뮬레이션 강제 / description len() 사전측정 / 세션ID system prompt 직추출.

## ⛔ 절대 규칙 (4)

| # | 규칙 |
|---|------|
| 1 | **게이트키퍼** — `mnt/.claude/skills/` 편집 전 본 스킬 발동. 미발동 = FAIL |
| 2 | **수정 완료 = `mnt/outputs/{skill}.skill` 1개 + host plugin path rsync** |
| 3 | **편집은 VM `/sessions/$SESSION_ID/$SKILL/`** — host 원본 read-only |
| 4 | **루프 max 2회** — 검증 실패 1회 재시도, 2회차 = STOP |

## ① 복사

**세션 ID = system prompt에서 직접 추출** (`ls /sessions/` ✗ — 권한 거부됨). 시스템 reminder의 `/sessions/{id}/mnt/` 경로에서 추출.

```bash
SESSION_ID=relaxed-wizardly-albattani  # system prompt에서 추출
SKILL=skill-name

rm -rf /sessions/$SESSION_ID/$SKILL && \
mkdir -p /sessions/$SESSION_ID/$SKILL && \
cp -r /sessions/$SESSION_ID/mnt/.claude/skills/$SKILL/* /sessions/$SESSION_ID/$SKILL/ && \
chmod -R u+w /sessions/$SESSION_ID/$SKILL/ && \
wc -l /sessions/$SESSION_ID/$SKILL/SKILL.md
```

**경로 판정 1줄:** 진단(검증해줘) / 경미(≤3곳) / 중간(섹션 신설) / 신규(처음부터) / 리팩토링(분량·구조 재설계).

## ② 묶음 편집·검증 (1회 heredoc)

**원칙: 편집·assert·len() 측정·grep 검증을 단일 heredoc에 묶는다.** 편집 후 `head·tail·grep` 재확인 ✗.

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

# 동일 heredoc 안 검증
m = re.search(r"^description: (.+)$", s, re.MULTILINE)
desc_len = len(m.group(1)) if m else 0
assert desc_len <= 1024, f"description {desc_len}/1024 초과"

print(f"edits={len(edits)} desc={desc_len}/1024 lines={s.count(chr(10))}")
EOF
```

**전면 재작성:** 단일 `python3` heredoc 안에서 `open(p,"w").write(new_content)` + 동일 heredoc에 검증.

**작성 권고 (사전 자가검토):** 본질·트리거(P1 5+/P2 한+영/P5 1+/NOT)·단일 책임·WRONG/CORRECT.

상세 — `→ references/edit-protocol.md`.

## ③ Dry-run 시뮬레이션 (패키징 직전 강제)

**v2.0 실패 본질:** "패키징 완료 = 끝"으로 보고했으나 실제 발동 시 스킬이 작동 안 함. 형이 사용하고서야 발견. v3.0은 패키징 *직전* 실제 발동 시 출력을 1회 시뮬레이션.

```bash
python3 /sessions/$SESSION_ID/skill-builder/scripts/dry_run.py /sessions/$SESSION_ID/$SKILL/
```

**검증:** validate.py errors=[] **AND** dry_run.py PASS 동시 충족.

```bash
cd /sessions/$SESSION_ID && \
python3 skill-builder/scripts/validate.py ./$SKILL/ | grep -E '"valid"|"errors"' && \
python3 skill-builder/scripts/dry_run.py ./$SKILL/
```

**컨펌 1줄 (패키징 직전):** `경로: {경미/중간/신규/리팩토링} · 변경 N · validate=OK · dry-run=PASS → 진행할까?` 형이 "끝까지·전부·일괄·리팩토링" 명시 시 Skip.

## ④ 패키징 + Host sync (단일 bash)

```bash
SESSION_ID=relaxed-wizardly-albattani; SKILL=skill-name
cd /sessions/$SESSION_ID && \
rm -f $SKILL.skill && \
zip -qr $SKILL.skill $SKILL/ -x "*.pyc" "__pycache__/*" ".DS_Store" "evals/*" && \
cp $SKILL.skill mnt/outputs/$SKILL.skill && \
bash skill-builder/scripts/sync-to-host-plugin.sh $SKILL && \
ls -la mnt/outputs/$SKILL.skill
```

**`sync-to-host-plugin.sh`:** `mnt/outputs/{skill}.skill` → host plugin path로 unzip+rsync. git-sync가 host 원본을 보기 때문에 필수.

**제공:** `[다운로드](computer://...)` 1줄. **git push 제안:** 옵션·답 없으면 ✗.

## 리서치 필요 스킬

**판정:** 외부 지식(법령·사례·통계) 필요 = 리서치. 결과는 **VAULT/_skills research/{skill}/{YYYY-MM-DD}_{topic}.md**. 세션·outputs 저장 ✗.

볼트 미마운트 + 리서치 필요 = `request_cowork_directory`. 거부 시 STOP+보고.

## 신규생성

```
skill-name/
├── SKILL.md          (≤500줄·목표 200~300)
├── references/       (도메인 지식 ≥1개)
├── scripts/          (결정적·반복 작업)
└── assets/           (출력 템플릿)
```

description ≤1024자·3인칭/명령형·"undertrigger" 방지로 적극적. 표 우선·"왜" 필수·예시 1+·Gotchas 필수.

상세 — `→ references/new-skill-template.md`, `→ references/trigger-guide.md`.

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

## Gotchas

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

## ✅ v2.0 → v3.0

| 결함 (v2.0) | 처방 (v3.0) |
|---|---|
| 편집→head→grep→ls 매 step 재확인 (~10턴/세션) | 묶음 heredoc 1회 — 편집·assert·len()·grep 단일 |
| VM↔Host 분단으로 git-sync "변경 없음" | `sync-to-host-plugin.sh` ④에 강제 |
| Dry-run 없음 → 실패 사후 적발 | `dry_run.py` 패키징 직전 강제·errors=[] AND PASS |
| description 한도 사후 적발 | heredoc 안 `len()` assert |
| `ls /sessions/` 권한 거부 후 1턴 낭비 | system prompt 직추출 |
| 본문 268줄·게이트 12+개 | 본문 180줄·게이트 2개 (경로판정·패키징직전) |
