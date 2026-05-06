---
name: skill-builder
version: 1.7.0
license: Proprietary. LICENSE.txt has complete terms
description: |
  스킬 수정·생성·패키징 **게이트키퍼** — mnt/.claude/skills/ 수정·생성 전 Skill tool 발동. **v1.7: Single-Confirm-Gate** — 컨펌게이트 3개→1개 통합(② 편집 후 dry-run 산출물 보고 1회). git push는 제안 1줄(게이트 ✗). **v1.6 Tool-Reach-Aware 보존**: 편집 도구 결정표·PREFLIGHT 도달성 체크·bash+python3 디폴트. **v1.5 사전생성형(PRE_WRITE_GUARD) 보존**: ② 편집 *진입 전* 5종 룰 강제. **리서치스킬 강제발동 + 리서치 VAULT 저장 강제**.
  P1: SKILL.md, 스킬수정, 스킬생성, 스킬업데이트, 스킬개선, 스킬패키징, 스킬검증, 트리거수정, 게이트키퍼, 리서치스킬, 리서치기반스킬, 사전가드, 작성가드, PRE_WRITE_GUARD, 도구도달성, 편집도구결정표, bash-python3편집, 단계컨펌게이트, batch dict패턴.
  P2: 만들어줘, 수정해줘, 고쳐줘, 바꿔줘, 업데이트, create, fix, update.
  P3: skill creation, skill modification, research-backed skill, pre-write guard.
  P4: SKILL.md·references/·scripts/ 편집, {스킬명}+수정동사, autoloop 완료.
  P5: .skill로, 리서치는 VAULT/_skills research/로.
  NOT: 프롬프트엔지니어링(→직접), 플러그인(→create-cowork-plugin), 최적화루프(→autoloop), UP수정(→up-manager).
vault_dependency: HARD  # 미마운트=STOP+보고. fallback 없음(SKILL 원본 접근 필수)
---

# Skill Builder

스킬 생성·수정·스킬패키징·스킬검증 1턴 게이트키퍼. 선형 흐름 — 분기 최소, 루프 0.
**v1.7 Single-Confirm-Gate:** 컨펌게이트 3개→1개 통합. ② 편집 후 dry-run 산출물(diff·판정·EDIT_MODE)을 1번에 보고 → 컨펌 → ③ 패키징. git push는 제안 1줄(게이트 ✗).
**v1.6 Tool-Reach-Aware 보존:** 편집 도구 결정표·PREFLIGHT 도달성·bash+python3 디폴트.
**v1.5 사전생성형 보존:** ② 편집 *진입 전* 5종 룰 강제. ②-b는 안전망 1회. 사후교정 의존 ✗.

**흐름:** 🚦 PREFLIGHT(+도달성) → ⓘ 리서치필요 판정 → 🅐 AskUserQuestion (불명확 시만) → ① 읽기+판정 → [진단이면 종료] → **②-PRE PRE_WRITE_GUARD (5종 활성화)** → ② 편집 [룰 강제된 상태로 작성] → ②-b 안전망 검증 → **🚦 단일 컨펌게이트 (편집 후 dry-run 산출물 보고)** → ③ 패키징+제공 → git push 제안 1줄(옵션)

---

## ⛔ 절대 규칙 (9개)

| # | 규칙 | 이유 |
|---|------|------|
| 1 | **게이트키퍼** — `mnt/.claude/skills/` 하위 **어떤 파일이든**(SKILL.md·references/·scripts/·assets/) 수정·생성·삭제·이름변경 전 **반드시 `Skill tool`로 skill-builder 발동**. 도구 무관(Edit/Write/Bash mv/Bash rm). **감지:** ①경로가 `mnt/.claude/skills/` 하위 ②대화에 스킬명+수정동사 ③"스킬 수정/고쳐/바꿔/업데이트" 언급 ④진단→수정 전환 ⑤EDIT4 직행 ⑥**리서치 필요 스킬 생성·수정** (도메인지식·사례·레퍼런스·벤치마킹 수집 선행) — 하나라도 걸리면 Skill tool 호출 먼저 | description이 발동 판단 유일 입력. 미발동 = 버전 꼬임·검증 누락·리서치 결과 세션 소실 |
| 2 | **수정 완료 = .skill 패키징 제공** | 사용자가 설치할 수 없음 |
| 3 | **세션 내 직접 편집** — 원본→세션 복사 → Cowork Edit/Write → zip → present. FS MCP는 plugin_skills_path 반영 시에만 | 세션 도구가 최단 경로. WORKBENCH 경유 = 이원화 병목 |
**📋 편집 도구 결정표 (v1.6 신설 — 매 편집 진입 전 1초 결정):** _도구도달성·편집도구결정표·bash-python3편집·단계컨펌게이트_

| 환경 | 대상 경로 | 편집 도구 | 비고 |
|------|----------|----------|------|
| Cowork mode | `mnt/.claude/skills/...` (read-only) | **bash + python3 in-place** | Cowork Edit 사각지대·DC도 VM 격리로 못 닿음. 디폴트 |
| Cowork mode | 형 컨넥티드 폴더 (예: VAULT) | **Cowork Edit/Write** | 정상 도달 |
| 호스트 마운트 | `/var/folders/...` (Mac 호스트) | **DC edit_block** | host fs 직접 |
| 세션 디렉터리 | `/sessions/{id}/{skill}/` (세션 복사본) | **bash + python3 in-place** | VM 안. Cowork Edit/DC 모두 못 닿음 |

**룰:** PREFLIGHT 도달성 체크에서 EDIT_MODE 출력 → 그 모드만 사용. 4번 갈아타기 = FAIL.

| 4 | **루프 하드캡** — 재시도·검증 순회 **max 2회**. 초과 → 보고 + STOP | 무한 루프 방지 |
| 5 | **원본 유일 = skills-plugin** — 매번 원본에서 새로. **예외: autoloop handoff** — 세션에 `handoff.json` 존재 시 오토루프 실험장을 원본으로 사용 | 버전 꼬임 방지. handoff는 오토루프 검증 완료 상태 |
| 6 | **PREFLIGHT 선행** — 착수 전 단일 Bash 1회로 경로·권한·출력경로 3체크 + 세션 복사본 Read 1회. 미수행 시 ① 진입 = FAIL | EROFS·Read 누락·출력경로 미존재 연쇄 실패 1턴 차단 |
| 7 | **리서치 결과 = VAULT 저장 강제** — 스킬 생성·수정 중 발생하는 **모든 리서치 산출물**(웹리서치·도메인분석·벤치마킹·사례수집·레퍼런스정리·WebSearch 결과)은 **무조건 VAULT에 저장**. 세션·`mnt/outputs/`·스크래치패드 저장 = FAIL. 볼트 미마운트 시 `request_cowork_directory`로 선마운트 → 거부 시 STOP+보고. 저장 경로: `VAULT/_skills research/{skill-name}/{YYYY-MM-DD}_{topic}.md`. SKILL.md 본문에는 요약·포인터만, 원본 리서치는 볼트에 | 세션 종료 = 리서치 전량 소실. 스킬은 재생성 가능하지만 리서치는 복구 불가 |
| 8 | **NO_WORK_LABEL 강제 주입** — 산출물 생성 스킬(P5에 `.md/.html/.docx/.pptx/.xlsx/.pdf` 포함, 또는 "산출물·보고서·기획안·제안서·문서·리포트" 직접 생성)을 **신규 생성·중간 수정**할 때 SKILL.md 흐름 직후 또는 절대규칙 첫 항목으로 `→ references/no-work-label-block.md`의 verbatim 블록을 **그대로 삽입**. 변형·요약·재배치 금지. ②-b 검증에서 누락 발견 = STOP + 재삽입. 경미 편집은 면제(이미 박혀있으면 통과) | 외부인이 사전 없이 못 읽는 작업 라벨(C:E:W:·Y2·4축 등) 산출물 누출 차단. 결정적 게이트(확률 ✗) |
| 9 | **PRE_WRITE_GUARD 사전생성형 (v1.5)** — ② 편집 *진입 전* 5종 룰 강제 활성화 → 룰 강제된 상태로 작성. ①본질질문(왜 이 스킬·룰이 필요한가, 기존 스킬로 안 되나) ②형식슬롯(P1·P2·P3·P5·NOT·Gotchas 사전 명시) ③트리거티어(P1 5+/P2 한+영/P5 1+/NOT 필수) ④단일책임(NOT 명시로 영토 분리) ⑤WRONG-CORRECT 1쌍. 사후교정으로 룰 적용 = FAIL. ②-b는 안전망 1회로 격하 (적발 시 ② 재진입, 루프 max 2회) | shaper-skill v3.1과 동일 본질. 사후교정형은 70% 쓰레기 잔존·토큰 낭비. 사전 강제가 본질 |

> **INV 9 — PRE_WRITE_GUARD 본질**
> ②-PRE 5종 활성화 후 ② 진입. 메커니즘: 사후교정 ✗·사전생성 ○. 자가검사 (편집 직전): "이 5종을 *지금* 적용하고 작성하나, 작성 후 적용하나?" 후자 = FAIL → ② 재진입.

---

## 🚦 PREFLIGHT (단일 Bash 1회)

```bash
echo "=== ① ORIGIN 경로·권한 ===" && ls -la mnt/.claude/skills/{skill}/SKILL.md 2>&1 | head -5 && \
echo "=== ② SKILL.md 개수 ===" && find mnt/.claude/skills/{skill}/ -name "SKILL.md" | wc -l && \
echo "=== ③ 출력 경로 ===" && ls -d mnt/*/ 2>&1 | grep -v uploads | grep -v .claude && \
echo "=== ④ EDIT_MODE 도달성 ===" && [ -w mnt/.claude/skills/{skill}/SKILL.md ] && echo "EDIT_MODE=cowork-edit" || echo "EDIT_MODE=bash-python3 (read-only/non-connected)"
```

| 체크 | 기준 | 실패 시 |
|------|------|---------|
| ① 경로·권한 | ORIGIN SKILL.md 존재·가독 | STOP + 스킬명 확인 요청 |
| ② SKILL.md 1개 | `wc -l` = 1 | STOP (2개+ 시 zip 충돌) |
| ③ 출력 경로 | 마운트 폴더 1개+ | 스크래치패드로 전환 |
| ④ EDIT_MODE | `cowork-edit` 또는 `bash-python3` 1개 출력 | 결정표 따라 그 도구만 사용. 다른 도구 시도 = FAIL·재진입 |

**Read-before-Edit 의무:** 세션 복사본을 Cowork Read로 1회 이상 읽고 Edit 착수. `cp + chmod`만으론 Cowork 파일추적 갱신 안 됨 → `File has not been read yet` 에러.

---

## ⓘ 리서치 필요 판정 + VAULT 저장 (규칙 #7)

**판정:** 스킬 생성·수정에 외부 지식 수집이 필요한가?
- 도메인 이론·법령·사례·벤치마크·레퍼런스·통계 등 **본문에 반영할 근거자료**가 필요하면 = **리서치스킬**(리서치기반스킬)
- 기존 SKILL.md 구조·트리거·문구만 손대는 경미 편집 = 리서치 불필요

**리서치 필요 시 강제 흐름:**
1. **VAULT 마운트 확인** → 없으면 `request_cowork_directory`로 VAULT 경로 마운트 요청. 거부 시 STOP+보고.
2. **저장 경로:** `VAULT/_skills research/{skill-name}/{YYYY-MM-DD}_{topic}.md`
   - 디렉토리 없으면 자동 생성
   - 파일명에 topic 슬러그 포함 (예: `2026-04-21_m&a-redflag-catalog.md`)
3. **저장 원칙:**
   - 원본 리서치(웹소스·raw 발췌·링크·인용문)는 **VAULT에만**
   - SKILL.md 본문에는 **요약 + 볼트 포인터** (`→ VAULT/_skills research/{skill-name}/... 참조`)
   - 세션·`mnt/outputs/`·스크래치패드에 리서치 자료 저장 = FAIL
4. **볼트 파일 frontmatter (필수):**
   ```yaml
   ---
   skill: {skill-name}
   date: YYYY-MM-DD
   topic: {topic-slug}
   sources: [url1, url2, ...]
   ---
   ```

**감지 키워드:** 리서치·조사·벤치마킹·사례·레퍼런스·도메인·최신동향·법령·통계·웹서치 — 하나라도 작업 맥락에 등장하면 리서치 필요 스킬로 판정.

---

## 🅐 AskUserQuestion (불명확 시만 — F2·F3 차용)

**조건:** PREFLIGHT 통과 후 다음 중 하나라도 모호:
- 스킬명 다중 후보 (formatter·formatter-skill·format-engine 등)
- "수정" 동사 모호 (트리거? description? 본문? 전부?)
- 신규 vs 수정 vs 진단 경계 모호

**Skip:** 형이 첫 메시지에 스킬명 + 수정 범위 + 동사 다 줬으면 직행. AskUserQuestion 호출 ✗·자유서술 ✗.

**호출 시:** AskUserQuestion 1회·options 명시 (자유서술 자동 포함). 답 받고 ① 진입.

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

**N개 동시 처리:** 독립 스킬이면 복사+Read+validate를 병렬 tool call. **batch 모드 = 단일 python3 1회로 N개 SKILL.md 동시 replace** (`→ references/bash-python3-edit-template.md` 참조).

---

## 🪧 판정 보고 (silent·1줄·게이트 ✗)

판정 직후 1줄 silent 보고 후 ②-PRE 직행. 컨펌 대기 ✗.

형식: `경로:{경미|중간|신규|진단} · EDIT_MODE:{bash-python3|cowork-edit|DC} · 예상갭:{N곳}`

**진단 경로:** 보고만 하고 종료.

---

## ②-PRE 사전 작성 가드 (v1.5, INV 9) — 사전가드·작성가드

② 편집 *진입 전* 5종 룰 활성화. 작성 단계 자체에 강제 적용 = **사전가드 = 작성가드** = PRE_WRITE_GUARD. **신규·중간 경로 강제. 경미는 ①·②만 적용.**

| # | 룰 | 사전 강제 (작성 전 답해야 ② 진입) | 사후 발견 시 |
|---|---|---|---|
| 1 | **본질 질문** | "이 스킬이 왜 필요한가? 기존 스킬로 안 되나? NOT 영토 어디?" | ② 재진입 |
| 2 | **형식 슬롯** | description에 P1·P2·P3·P5·NOT 사전 슬롯 명시. 작성 중 슬롯 채우기 | ② 재진입 |
| 3 | **트리거 티어** | P1 5+개·P2 한+영 2+개·P3 2+개·P5 1+개·NOT 필수 사전 결정 | ② 재진입 |
| 4 | **단일 책임** | NOT 라우팅 명시. 인접 스킬과 영토 분리. 중복 ✗ | ② 재진입 |
| 5 | **WRONG/CORRECT** | ❌WRONG/✅CORRECT 대조 1쌍 사전 강제 (Gotchas 또는 본문) | ② 재진입 |

**메커니즘:** 5종 답을 *먼저* 확정 → 그 답으로 SKILL.md 작성. "쓰고 나서 채운다" = FAIL. shaper-skill v3.1 §B-PRE와 동일 패턴.

**경미 편집 면제:** 수정 개소 ≤3 + 구조 동일 = 본 가드 스킵. 단 description 수정은 ①·②만으로도 통과.

**자가검사 (② 진입 직전):** "이 5종을 *지금* 적용하고 작성하나, 작성 후 적용하나?" 후자 = FAIL → ② 재진입.

---

## ② 편집

| 경로 | 할 일 | 도구 | 다음 |
|------|-------|------|------|
| 경미 | 해당 부분만 수정. description 변경 필요 시 같은 턴에 갱신 | Cowork Edit | validate.py만. 성능게이트 스킵 → ③ |
| 중간 | ②-PRE 5종 통과 후 구조 변경 + description 갱신 | Cowork Edit/Write | ②-b |
| 신규 | ②-PRE 5종 통과 후 의도→트리거→작성. `→ references/new-skill-template.md`, `→ references/trigger-guide.md` | Cowork Write | ②-b |

편집 대상: 세션(`/sessions/{session-id}/{skill}/`).

---

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
| 6 | NO_WORK_LABEL 블록 (산출물 스킬만) | `grep -q "\[NO_WORK_LABEL\]" SKILL.md` | `→ references/no-work-label-block.md` verbatim 삽입 |

---

## 🚦 단일 컨펌게이트 — 편집 후 dry-run 산출물 보고 (v1.7·F8 차용)

② 편집 + ②-b 통과 직후. 유일한 컨펌게이트. trigger-skill v5.6 dry-run 본질 = 실측 산출물 1회 보고 → 컨펌 → 패키징.

```
경로: {경미|중간|신규} · EDIT_MODE: {bash-python3|cowork-edit|DC}
변경 슬롯 N개:
- 슬롯 A: {Before 1줄} → {After 1줄}
- 슬롯 B: ...
검증: validate.py errors=[]
→ 패키징 진행할까?
```

**Skip 조건:** 형이 사전에 "끝까지 가" 명시 = Skip. 디폴트 = 컨펌 대기. 경미 편집 + 단일 슬롯 = 자동 Skip 가능.

**적발 시 ② 재진입:** 형이 "X도 추가" 등 수정사항 주면 ②로 복귀. 루프 max 2회.

---

## ③ 패키징 + 제공

상세: `→ references/packaging-guide.md`

**핵심 순서:** ③-a 선삭제(세션+mnt/outputs 양쪽) → ③-b zip → ③-c present_files → ③-d 검증(1개·접미사 없음)

| 단계 | 한 줄 요약 |
|---|---|
| ③-a | `rm -f {skill}.skill`·mnt 구파일 존재 시 `allow_cowork_file_delete` |
| ③-b | `zip -r {skill}.skill {skill}/ -x "*.pyc" "__pycache__/*" ".DS_Store" "evals/*"` |
| ③-c | 스크래치패드 `/sessions/{id}/{skill}.skill` → `present_files` (기본) |
| ③-d | `ls mnt/outputs/{skill}*.skill` = 1개·접미사 없음 |

**절대:** `-1`·`_copy` 접미사 = FAIL → ③-a 재실행. 루프 하드캡 2회.
**📌 패키징 완료 후 제안 (v1.7·게이트 ✗):** "git push 할까?" 1줄 옵션 제안. 형 답 없으면 발동 ✗·기다리지 않음. 게이트 아님.

---

## 신규생성 요약

**Start small (F10 차용):** 최소 컴포넌트로 시작. 한 스킬에 한 책임. references·scripts·assets는 필요할 때만.

**컴포넌트 플랜 표 (F4 차용·신규생성 시 컨펌게이트 1에서 출력):**

| 구성 | 만들/안 만들 | 이유 |
|------|------------|------|
| SKILL.md | 만든다 | 필수 |
| references/ | {O|X} | 도메인 지식·예시 필요 시 |
| scripts/ | {O|X} | 결정적·반복 작업 코드화 시 |
| assets/ | {O|X} | 출력 템플릿 필요 시 |

허브스포크: `→ references/hub-spoke-guide.md`
스켈레톤: `→ references/new-skill-template.md`
트리거: `→ references/trigger-guide.md`

**트리거 티어 (최소):** P1 5+ / P2 2(한+영) / P3 2+ / P4 0-2 / P5 1+ / NOT 필수
**Lean 기준:** SKILL.md 목표 5KB·최대 10KB·≤500줄 (Anthropic) / 표 우선 / 결정적 작업은 scripts/ (Anthropic) / "왜" 필수 / 예시 1+ / Gotchas 필수 / ❌WRONG/✅CORRECT 대조 권장
**description은 적극적으로** — Claude는 스킬을 덜 쓰는 쪽으로 편향. 범위를 넓혀라. 단 모호 동사("Helps with"·"Processes"·"Handles") 금지, 3인칭/명령형, ≤1024자 (Anthropic 공식).

```
skill-name/
├── SKILL.md          (필수)
├── references/       (필요시 로딩)
├── scripts/          (결정적·반복적 작업 코드화)
└── assets/           (출력용)
```

---

## 배치 모드 (v1.6 구체화·N4)

2개+ 스킬 동시 요청 시 = **단일 python3 1회 dict 처리**.

**원칙:** Read N개 병렬 → bash 1회로 dict {skill_name: [(old, new), ...]} 처리 → zip N개 병렬 → present_files 1회.

**금지:** 스킬마다 bash 따로·Edit 따로 = 4번 갈아타기 N배. 자동 FAIL.

**풀템플릿:** `→ references/bash-python3-edit-template.md`

```bash
# 단일 turn 패턴
cd /sessions/{id} && python3 - << 'INNER'
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
# 그 다음 zip 병렬
for sk in skill-A skill-B; do (cd /sessions/{id} && zip -r "$sk.skill" "$sk/" -x "*.pyc" "__pycache__/*" ".DS_Store") & done; wait
```

---

## Gotchas (외부 함정 전용 — 본문 규칙 복제 금지)

| 함정 | 대응 |
|------|------|
| `mnt/.claude/skills/` 직접 쓰기 | 읽기전용. 세션 복사 후 편집 → .skill 설치로만 반영 |
| Cowork Edit이 `mnt/.claude/skills/` 못 닿음 (v1.6 새 함정) | EDIT_MODE=bash-python3 강제. 결정표 참조. 4번 갈아타기 = FAIL |
| `/tmp/` 경로 | Read/Edit 접근 불가. 세션 디렉토리만 |
| WORKBENCH(`_skills workspace/`) 경유 | 불필요. FS MCP vs Cowork 경로 이원화로 병목 |
| description↔본문 불일치 | description이 발동 판단 유일 입력. 수정 시 본문 동기 확인 |
| zip 대신 tar | .skill은 zip만. tar = 설치 실패 |
| FS MCP 집착·순차 처리 | 세션 도구(Read/Write/Edit/Bash) 우선. 독립 스킬은 병렬 tool call |
| SKILL.md 2개 | zip 전 `find {skill}/ -name "SKILL.md" \| wc -l`로 1 확인 |
| handoff.json 있는데 skills-plugin 복사 | 오토루프 최적화 결과 덮어씀. ①.0 핸드오프 감지 먼저 |
| `.skill` 파일에 `-1`·`-2` 접미사 자동 부착 | 마운트 구파일 미삭제 → Cowork/Mac 덮어쓰기 회피 로직 작동. ③-a 선삭제 필수(세션 + mnt/outputs 양쪽) |
| 패키징 반복 실패·설치 후 동작 이상 | 원인 재현 불가 시 thumbs-down으로 Anthropic 피드백. CHANGELOG.md에 실패 유형·재현조건 기록 |
| 리서치 자료를 세션·`mnt/outputs/`에 저장 | 세션 종료 시 전량 소실. 규칙 #7 위반 = FAIL. 반드시 VAULT로. 볼트 미마운트 시 request_cowork_directory 선행 |
| VAULT 마운트 허락 없이 WebSearch 결과를 스킬 본문에 직접 붙여넣기 | 원본 소실·출처 단절. 볼트 저장 후 포인터로 연결 |
| 산출물 스킬에 NO_WORK_LABEL 블록 미주입·요약·변형 | 작업 라벨 누출 = 외부 독자 차단. verbatim 삽입 강제, 변형 시 ②-b에서 차단 |
| **사후교정 의존 (작성 후 ②-b에서 룰 적용)** | INV 9 위반. ②-PRE 5종을 *작성 전* 활성화. ②-b는 안전망 1회. 사후 적발 시 ② 재진입 |
| ②-PRE 5종 일부 스킵 ("쓰고 나서 채울게") | 사전생성형 본질 위배 → 70% 쓰레기 잔존. 5종 답 확정 후 ② 진입 |
