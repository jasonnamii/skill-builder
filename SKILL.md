---
name: skill-builder
version: 2.0.0
license: Proprietary. LICENSE.txt has complete terms
description: |
  스킬 생성·수정·스킬패키징·스킬검증 게이트키퍼. **v2.0 단순화 (공식 skill-creator 패턴 회귀):** 작업공간 4종→2종(`/tmp/{skill}/` 편집 + `mnt/outputs/` 산출), EDIT_MODE 결정표 폐기(bash-python3 단일), 게이트 12개→2개(경로판정 1줄 + 패키징 직전 dry-run 1줄). 절대규칙 9→4. 1턴 완결.
  P1: SKILL.md, 스킬수정, 스킬생성, 스킬업데이트, 스킬개선, 스킬패키징, 스킬검증, 트리거수정, 게이트키퍼, 리서치기반스킬, 스킬빌더, skill builder, skill creator.
  P2: 만들어줘, 수정해줘, 고쳐줘, 바꿔줘, 업데이트, create, fix, update.
  P3: skill creation, skill modification, research-backed skill, skill packaging.
  P4: SKILL.md·references/·scripts/ 편집, {스킬명}+수정동사, autoloop 완료.
  P5: .skill로, 리서치는 VAULT/_skills research/로.
  NOT: 프롬프트엔지니어링(→직접), 플러그인(→create-cowork-plugin), 최적화루프(→autoloop), UP수정(→up-manager).
vault_dependency: SOFT  # 리서치 스킬일 때만 강제. 일반 편집은 미마운트도 진행.
---

# Skill Builder v2.0

스킬 생성·수정·패키징 1턴 완결. **단순·선형 — 분기 최소·게이트 최소.**

**v2.0 원칙 (공식 skill-creator 회귀):**
- 작업공간 = `/tmp/{skill}/` 편집 + `mnt/outputs/` 산출. 끝.
- 도구 = `bash + python3 in-place`. 다른 분기 ✗.
- 게이트 = 경로판정 1줄 + 패키징 직전 dry-run 1줄. 그 외 ✗.
- 룰 = "explain why, not heavy MUSTs" — 본문 권고 우선·MUST 최소.

**흐름:** ① 복사+Read → ② 편집 → ③ validate+컨펌 → ④ zip+제공

---

## ⛔ 절대 규칙 (4개)

| # | 규칙 | 이유 |
|---|------|------|
| 1 | **게이트키퍼** — `mnt/.claude/skills/` 하위 파일을 수정·생성·삭제하기 전 반드시 `Skill tool`로 skill-builder 발동. 감지: 경로/스킬명+수정동사/"스킬 수정·고쳐·바꿔·업데이트"/리서치 필요 스킬 — 하나라도 hit | 미발동 = 버전 꼬임·검증 누락 |
| 2 | **수정 완료 = .skill 패키징 제공** — `mnt/outputs/{skill}.skill` 1개 (접미사 ✗). 없으면 형이 설치 못 함 | 사용자 설치 가능성이 본질 |
| 3 | **편집은 `/tmp/{skill}/`에서만** — 원본(`mnt/.claude/skills/`)은 read-only. cp → bash + python3 in-place → zip → outputs 복사. 경로 헷갈림 = FAIL의 80% | 작업공간 단일화 |
| 4 | **루프 max 2회** — 검증 실패 시 1회 재시도. 2회차 실패 = STOP + 보고 | 무한 루프 차단 |

> **그 외(PRE_WRITE_GUARD·NO_WORK_LABEL·VAULT 강제 등) = 본문 권고로 격하.** 사후교정 차단보다 사전 권고가 먼저. v1.7의 "9개 절대규칙"은 LLM이 매 스텝 자기점검 → 토큰 낭비 + 뱅뱅 돎.

---

## 🚦 PREFLIGHT (단일 Bash 1회)

```bash
SESSION_ID=$(ls /sessions/ 2>/dev/null | head -1)  # 또는 형이 명시한 세션 ID
SKILL=skill-name

# ① 원본 존재 ② SKILL.md 1개 ③ 출력경로 ④ /tmp 사용 가능
ls -la /sessions/$SESSION_ID/mnt/.claude/skills/$SKILL/SKILL.md && \
[ "$(find /sessions/$SESSION_ID/mnt/.claude/skills/$SKILL/ -name SKILL.md | wc -l)" = "1" ] && echo "OK SKILL.md 1개" && \
ls -d /sessions/$SESSION_ID/mnt/outputs/ && \
echo "EDIT_MODE=bash-python3 (단일·고정)"
```

**실패 시:** 원본 없음 → 스킬명 확인 / SKILL.md 2개+ → STOP / outputs 없음 → request_cowork_directory.

---

## ① 복사 + Read

**한 번에 전부:**
```bash
SESSION_ID=hopeful-youthful-knuth  # ls /sessions/ | head -1로 자동
SKILL=skill-name

mkdir -p /sessions/$SESSION_ID/$SKILL && \
cp -r /sessions/$SESSION_ID/mnt/.claude/skills/$SKILL/* /sessions/$SESSION_ID/$SKILL/ && \
chmod -R u+w /sessions/$SESSION_ID/$SKILL/
```

**Read:** Cowork Read로 `/sessions/$SESSION_ID/$SKILL/SKILL.md` 1회. (Cowork 파일추적 갱신 필요 — cp+chmod만으론 부족)

**경로 판정 (1줄·자가확정):**

| 경로 | 조건 | 다음 |
|---|---|---|
| **진단** | "진단해줘·검증해줘" | validate.py 결과 보고 → 종료 |
| **경미** | 수정 ≤3곳·구조 동일 | ② |
| **중간** | 섹션 신설·로직 변경 | ② |
| **신규** | 처음부터 | ② → `→ references/new-skill-template.md` |

**핸드오프 감지:** `/sessions/$SESSION_ID/autoloop-lab/$SKILL/handoff.json` 존재 → ① 스킵, autoloop 결과를 원본으로 직행.

---

## ② 편집 (bash + python3 in-place)

**단일 패턴 (이것만 쓴다):**
```bash
cd /sessions/$SESSION_ID && python3 << 'INNER'
p = "skill-name/SKILL.md"
s = open(p).read()
edits = [
    ("OLD 1", "NEW 1"),
    ("OLD 2", "NEW 2"),
]
for o, n in edits:
    assert o in s, f"missing: {o[:40]}"
    s = s.replace(o, n, 1)
open(p, "w").write(s)
INNER
```

**전면 재작성:** `cat > $SKILL/SKILL.md << 'EOF' ... EOF` 단일 heredoc.

**신규생성:** `→ references/new-skill-template.md` 참조 후 cat heredoc.

**작성 권고 (사전 자가검토 — MUST ✗·권고 ○):**
1. 본질 — 왜 이 스킬·룰이 필요한가? 기존 스킬로 안 되나? NOT 영토는?
2. 트리거 — P1 5+개·P2 한+영 2+개·P5 1+개·NOT 필수
3. 단일 책임 — NOT 라우팅으로 인접 스킬과 영토 분리
4. WRONG/CORRECT — Gotchas 또는 본문에 1쌍

> 사후 ②-b 안전망보다 작성 *전* 자가검토가 토큰·품질 모두 우월. 단 사후교정 발견 시 1회 재진입(루프 cap).

---

## ③ 검증 + 컨펌게이트 (단일·1줄)

**검증:**
```bash
cd /sessions/$SESSION_ID && python3 skill-builder/scripts/validate.py ./$SKILL/
# errors=[] → 통과
```

**유일한 컨펌게이트 (패키징 직전·1줄):**
```
경로: {경미|중간|신규} · 변경 N곳 · validate=OK
→ 패키징 진행할까?
```

**Skip 조건:** 형이 "끝까지·전부·일괄" 명시 시 디폴트 Skip → ④ 직행. 명시 없으면 컨펌 대기.

**적발 시:** 형이 "X 추가" → ②로 복귀. 루프 max 2회.

---

## ④ 패키징 + 제공

**단일 bash 1콜:**
```bash
SESSION_ID=hopeful-youthful-knuth; SKILL=skill-name; \
rm -f /sessions/$SESSION_ID/$SKILL.skill /sessions/$SESSION_ID/mnt/outputs/$SKILL.skill && \
cd /sessions/$SESSION_ID && \
zip -qr $SKILL.skill $SKILL/ -x "*.pyc" "__pycache__/*" ".DS_Store" "evals/*" && \
cp $SKILL.skill mnt/outputs/$SKILL.skill && \
ls -la mnt/outputs/$SKILL.skill
```

**검증 1줄:** `mnt/outputs/{skill}.skill` 1개 + 접미사 없음 (`-1`·`_copy` ✗ → 재실행).

**제공:** `[다운로드](computer://...)` 링크 1줄.

**git push 제안 (옵션·게이트 ✗):** "git push 할까?" 1줄. 답 없으면 발동 ✗.

---

## 리서치 필요 스킬 (조건부)

**판정:** 스킬 본문에 외부 지식(법령·사례·벤치마크·통계)이 들어가야 하면 = 리서치 필요.

**리서치 발생 시:** 결과는 **VAULT/_skills research/{skill}/{YYYY-MM-DD}_{topic}.md**에 저장. 세션·outputs 저장 ✗ (세션 종료 시 소실).

볼트 미마운트 + 리서치 필요 = `request_cowork_directory`로 마운트 요청. 거부 시 STOP+보고.

리서치 불필요한 일반 편집(트리거·구조·문구) = VAULT 무관·진행.

---

## 신규생성 (간략)

```
skill-name/
├── SKILL.md          (필수)
├── references/       (도메인 지식 ≥1개일 때만)
├── scripts/          (결정적·반복 작업 ≥1개일 때만)
└── assets/           (출력 템플릿 필요할 때만)
```

**Lean 기준 (Anthropic 공식):**
- SKILL.md ≤500줄 (목표 200~300)
- description ≤1024자·3인칭/명령형·"undertrigger" 방지로 적극적
- "Helps with·Processes·Handles" 같은 모호 동사 ✗
- 표 우선·결정적 작업은 scripts/·"왜" 필수·예시 1+·Gotchas 필수·WRONG/CORRECT 권장

**트리거 티어:** P1 5+ / P2 2(한+영) / P3 2+ / P4 0~2 / P5 1+ / NOT 필수.

스켈레톤·트리거 상세: `→ references/new-skill-template.md`, `→ references/trigger-guide.md`.

---

## 배치 모드 (N개 동시)

2개+ 스킬 = **단일 python3 1회 dict**:

```bash
cd /sessions/$SESSION_ID && python3 << 'INNER'
edits = {
  "skill-A": [("old1", "new1"), ("old2", "new2")],
  "skill-B": [("oldX", "newY")],
}
for skill, pairs in edits.items():
    p = f"{skill}/SKILL.md"
    s = open(p).read()
    for o, n in pairs:
        assert o in s, f"{skill}: missing {o[:40]}"
        s = s.replace(o, n, 1)
    open(p, "w").write(s)
INNER

# zip 병렬
for sk in skill-A skill-B; do
  (cd /sessions/$SESSION_ID && zip -qr "$sk.skill" "$sk/" -x "*.pyc" "__pycache__/*" ".DS_Store") &
done; wait
```

---

## ✅ WRONG / CORRECT

❌ **WRONG (v1.7 — 작업공간 4종 동시):**
```
mnt/.claude/skills/{skill}/  (read-only 원본)
/sessions/{id}/{skill}/      (세션 복사본)
mnt/outputs/                 (산출)
VAULT/_skills research/      (리서치)
+ EDIT_MODE 4종 결정표 (cowork-edit · bash-python3 · DC · 세션)
→ LLM이 host vs VM path 헷갈림 → cp 다시 → chmod 다시 → 재진입 N회
```

✅ **CORRECT (v2.0 — 단일화):**
```
편집: /tmp 대신 /sessions/{id}/{skill}/ (VM 단일)
산출: mnt/outputs/{skill}.skill
도구: bash + python3 in-place 단일
→ 분기 0개·재진입 0건
```

❌ **WRONG (v1.7 — 게이트 12개):**
```
PREFLIGHT 4체크 → ②-PRE 5종 → ②-b 안전망 → 단일 컨펌 → 패키징 4단계
→ LLM이 매 스텝 "지금 어느 게이트?" 자기점검 → 토큰 낭비
```

✅ **CORRECT (v2.0 — 게이트 2개):**
```
경로 판정 1줄 (진단/경미/중간/신규)
패키징 직전 1줄 (컨펌 또는 Skip)
끝.
```

---

## Gotchas

| 함정 | 대응 |
|---|---|
| `mnt/.claude/skills/` 직접 쓰기 | 읽기전용. 세션 복사 후 편집 → .skill 설치로만 반영 |
| host path vs VM path 혼동 | 모든 작업은 VM `/sessions/$SESSION_ID/` 안에서. host `/Users/...` ✗ |
| `cp + chmod`만 하고 Read 안 함 | Cowork 파일추적 미갱신 → "File has not been read yet" 에러. Read 1회 필수 |
| `.skill` 접미사 `-1`·`_copy` 자동 부착 | 마운트 구파일 미삭제 → 회피 로직 작동. ④에서 양쪽 선삭제 (`rm -f session/$SKILL.skill mnt/outputs/$SKILL.skill`) 필수 |
| `find {skill}/ -name SKILL.md \| wc -l` ≠ 1 | zip 충돌. 수정 또는 삭제 후 재시도 |
| zip 대신 tar | .skill = zip 전용. tar = 설치 실패 |
| autoloop handoff 무시하고 원본 복사 | 오토루프 최적화 결과 덮어씀. ① 시작 시 handoff.json 감지 먼저 |
| 리서치를 세션·outputs에 저장 | 세션 종료 = 전량 소실. 리서치는 VAULT만 |
| description ↔ 본문 불일치 | description이 발동 판단 유일 입력. 수정 시 본문 동기 필수 |
| 게이트마다 컨펌 대기 | v2.0은 경로판정 + 패키징 직전 2개만. 그 외 silent 진행 |
