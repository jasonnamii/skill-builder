---
name: skill-builder
description: "스킬 생성·수정·패키징 유일한 게이트키퍼. 스킬 파일을 수정·제작하려면 반드시 이 스킬을 먼저 발동해야 함. 스킬빌더 없이 직접 스킬 수정 시도 = FAIL. 트리거 설계부터 Lean 작성, 검증, .skill 패키징까지 전 과정 수행. 스킬 만들기·수정·패키징·검증 요청시 발동."
"@uses":
  - references/trigger-guide.md
---

<!-- Triggers
P1: 스킬, skill, SKILL.md, 패키징, 검증, 스킬만들기, 스킬수정.
P2: 만들어줘, 수정해줘, 고쳐줘, validate, create, fix.
P3: skill creation, skill modification, description optimization.
P5: .skill로.
NOT: 프롬프트엔지니어링(→직접), 플러그인(→create-cowork-plugin), 스킬최적화루프(→autoloop), 다른 스킬 단순 사용(→해당 스킬).
GATE: 스킬 파일 수정·제작에만 발동. 스킬 사용 ≠ 스킬 수정.
-->

# Skill Builder

스킬 생성·수정·패키징 오케스트레이터. **속도 최우선 — 병렬·배치·스킵을 적극 활용.**

---

## ⛔ 절대 규칙

| # | 규칙 |
|---|------|
| 1 | **병렬 최대화** — 의존관계 없는 스킬은 **최대 4개 동시** 처리. 읽기·복사·편집 각각을 병렬 tool call로 발행. 경미수정은 배치 모드로 1턴 일괄 |
| 2 | **수정 완료 = .skill 패키징 제공** — 패키징 없이 "수정했습니다"는 미완료 |
| 3 | **경로는 세션 디렉토리만** — `/tmp/` 사용 금지. Read/Edit tool이 접근 못 해서 뺑뺑이의 원인 |
| 4 | **게이트키퍼** — 스킬 SKILL.md를 수정·제작할 때 **반드시 skill-builder를 먼저 발동**. skill-builder 미발동 상태에서 스킬 파일 수정 착수 = FAIL. 단, 다른 스킬이 대화에서 단순 '사용/발동'되는 것에는 관여하지 않음 — 오직 스킬 파일 편집·제작 시에만 |

---

## 속도 원칙 (모든 경로에 적용)

| 원칙 | 구현 방법 | 이유 |
|------|----------|------|
| **병렬 읽기** | 대상 스킬 N개의 SKILL.md를 **1턴에 N개 Read tool call** 동시 발행 | 순차 읽기는 N턴 낭비 |
| **병렬 복사** | `cp -r A ./ & cp -r B ./ & wait` 또는 N개 Bash call 동시 | 복사도 독립 작업 |
| **병렬 편집** | 서로 다른 파일의 Edit을 **1턴에 최대 6개** 동시 발행 | Cowork Edit tool은 파일별 독립 |
| **병렬 패키징** | N개 스킬의 zip을 **1개 Bash에 `&`+`wait`** 또는 N개 Bash call 동시 | 패키징도 독립 작업 |
| **단계 합치기** | 편집+description 검사를 동일 Edit에서 처리 (별도 턴 X) | 왕복 1회 절감 |
| **조건부 스킵** | 경미수정에서 description 미변경 시 동기 검사 스킵 | 불필요한 LLM 판단 제거 |

---

## 4경로 분기

| 경로 | 조건 | 실행 단계 | 스킵 |
|------|------|----------|------|
| **경미수정 FAST** | 지시 1-3줄, 섹션 구조 동일, description 변경 불필요 | 읽기→편집→패키징→제공 **(3턴)** | description 검사, 검증, 테스트 |
| **경미수정** | 지시 1-3줄, 섹션 구조 동일, description 변경 필요 | 읽기→편집+description 갱신→패키징→제공 **(3턴)** | 검증, 테스트 |
| **중간수정** | 섹션 신설·삭제·재배치, 레퍼런스 추가, 로직 변경 | 읽기→편집+description 갱신→검증→패키징→제공 | 테스트 |
| **신규생성** | 스킬을 처음부터 만듦 | 설계(의도→트리거→작성)→검증→패키징→제공 | 테스트 (사용자 명시 시만) |

**판정:** 수정 개소 3 이하 + 섹션 동일 = 경미. 그 외 = 중간. 새 스킬 = 신규.

---

## 배치 모드 (N개 스킬 동시 처리)

여러 스킬을 수정할 때의 실행 패턴. **핵심: 같은 유형의 단계를 모아서 병렬 발행.**

```
턴1: Read(A) + Read(B) + Read(C) + Read(D)     ← 병렬 읽기 (최대 4개)
턴2: Bash(cp A & cp B & cp C & cp D & wait)     ← 병렬 복사 (1 Bash)
턴3: Edit(A) + Edit(B) + Edit(C) + Edit(D)      ← 병렬 편집 (최대 6개)
턴4: Bash(zip A & zip B & zip C & zip D & wait)  ← 병렬 패키징 (1 Bash)
     + cp *.skill mnt/outputs/
턴5: 링크 제공
```

**배치 적용 조건:** 2개 이상 스킬이 같은 경로(경미/중간)일 때. 경로가 다르면 같은 경로끼리 묶어 배치.

---

## 수정 경로 (경미 + 중간 공통)

### 1. 읽기 (병렬)

```bash
# 여러 스킬이면 Read tool을 N개 동시 발행
# 단일이면 1개
cat /sessions/*/mnt/.claude/skills/{skill-name}/SKILL.md
```

### 2. 세션 복사 + 편집

```bash
# 세션 루트로 복사 — 여러 스킬이면 & 로 병렬
cp -r mnt/.claude/skills/{skill-A} ./{skill-A}/ &
cp -r mnt/.claude/skills/{skill-B} ./{skill-B}/ &
wait
chmod -R u+w ./{skill-A}/ ./{skill-B}/
```

Edit tool로 수정. **동시에 여러 파일의 Edit을 1턴에 발행** (파일별 독립이므로 안전).

### 3. description 동기 검사 (조건부)

| 조건 | 행동 |
|------|------|
| 본문 수정이 description 범위(기능·수치·적용범위)에 영향 없음 | **스킵** — 편집 턴에서 판단 완료 |
| 본문 수정이 description에 영향 있음 | 편집과 **같은 턴**에 description도 Edit으로 갱신 |

### 4. 검증 체크리스트 (중간수정 + 신규만)

LLM이 직접 확인. 하나라도 실패 → 수정:

- [ ] YAML frontmatter 형식 (`---`로 시작/종료)
- [ ] name: lowercase+hyphens, 64자 이내
- [ ] description: 500자 이내
- [ ] YAML에 탭 문자 없음
- [ ] P1 5개+, P2 2개+, P3 2개+, P5 1개+, NOT 존재
- [ ] SKILL.md ≤ 10KB
- [ ] 기존 스킬과 P1 키워드 충돌 없음

**Python 자동 검증** (스킬에 scripts/ 포함 시):
```bash
python -m scripts.quick_validate {skill-directory}
```

### 5. 패키징 + 제공 (병렬)

```bash
# 여러 스킬이면 병렬 zip
cd /sessions/quirky-fervent-goldberg
zip -r {skill-A}.skill {skill-A}/ -x "*.pyc" -x "__pycache__/*" -x ".DS_Store" -x ".git/*" -x "*-workspace/*" -x "evals/*" &
zip -r {skill-B}.skill {skill-B}/ -x "*.pyc" -x "__pycache__/*" -x ".DS_Store" -x ".git/*" -x "*-workspace/*" -x "evals/*" &
wait

# 구조 검증 + 배포 (한 번에)
for f in {skill-A}.skill {skill-B}.skill; do
  unzip -l "$f" | head -5
  cp "$f" mnt/outputs/
done
```

computer:// 링크로 제공. 파일명 = `{skill-name}.skill` 고정. 버전명·접미사 금지.

---

## 신규생성 경로

### 설계

#### 의도 파악

1. 이 스킬이 Claude에게 뭘 가능하게 하는가?
2. 언제 트리거되어야 하는가?
3. 기대 출력 형식은?

#### 트리거 설계

`references/trigger-guide.md`를 읽고 P1-P5+NOT 체계를 적용.

| 티어 | 역할 | 최소 요건 |
|------|------|----------|
| P1 | 고유 키워드 (명사) | 5개+ |
| P2 | 동사 패턴 | 2개 (한+영) |
| P3 | 영어 기술용어 | 2개+ |
| P4 | 상황적 표현 | 0-2개 (선택) |
| P5 | 출력 형태 | 1개+ |
| NOT | 제외 + 라우팅 | 필수 |

**description은 적극적으로** — Claude는 스킬을 덜 쓰는 쪽으로 편향됨. 범위를 넓혀라. 기존 스킬 P1 키워드 겹침 확인 필수.

#### SKILL.md 작성

**스킬 구조:**
```
skill-name/
├── SKILL.md (필수)
│   ├── YAML frontmatter (name, description 필수)
│   └── Markdown 본문
└── Bundled Resources (선택)
    ├── scripts/    - 결정적/반복 작업용 실행 코드
    ├── references/ - 필요시 컨텍스트에 로딩되는 문서
    └── assets/     - 출력에 사용되는 파일
```

**Lean 원칙:**

| 원칙 | 기준 |
|------|------|
| SKILL.md 크기 | 목표 5KB, 최대 10KB |
| 표 우선 | 설명 → 표로 압축 |
| 코드 최소 | 패턴만, 20줄 이내 |
| 중복 제거 | 같은 내용 1회만 |

**허브+스포크 패턴:** 복잡한 스킬은 SKILL.md를 허브로 두고 세부내용을 references/로 분리.

**작성 규칙:** "왜" 설명 필수(이유 없는 지시→무시), 예시 1개+(없으면 출력 자의적), Gotchas 섹션 필수, ALWAYS/NEVER 남발 대신 이유 설명.

작성 완료 → 검증 체크리스트(위) → 패키징+제공(위).

---

## Gotchas

- **볼트 직접배포 함정:** Cowork의 mnt/.claude/skills/는 읽기전용 마운트. 볼트에 SKILL.md를 복사해도 런타임에 반영 안 됨. 유일한 경로는 .skill 패키지 빌드→Cowork에 재설치.
- **`/tmp/` 경로 함정:** Read/Edit tool은 세션 디렉토리 내에서만 안정 동작. `/tmp/`에 복사하면 Edit 실패 → Bash sed 우회 → 경로 혼선 → 재작업 루프. 세션 디렉토리에서만 작업.
- **description ↔ 본문 불일치:** 본문을 수정하면서 frontmatter description을 안 바꾸는 패턴. description이 발동 판단의 유일한 입력이므로, 불일치 시 발동 오류.
- **볼트 경로 탐색 루프:** DC start_search로 .claude/skills/ 경로를 찾으려 시도 → 히든 폴더 접근 거부 → 재탐색 → 시간 낭비. 읽기는 Cowork 마운트, 쓰기는 세션 카피. 탐색 자체를 시도하지 않는다.
- **zip이 아닌 tar.gz:** .skill은 zip이어야 한다. `tar -czf`로 만들면 "invalid zip" 에러.
- **순차 처리 함정:** 스킬 A 패키징 완료까지 기다린 후 스킬 B 읽기 시작하는 패턴. 독립 스킬은 반드시 병렬 tool call로 동시 처리. 순차로 빠지면 턴 수가 N배로 늘어난다.
- **단일 Edit 턴 함정:** 1턴에 Edit 1개만 발행하는 패턴. Cowork은 1턴에 최대 6개 Edit을 병렬 지원. 서로 다른 파일이면 무조건 묶어 발행.
- **오발동 함정:** 다른 스킬이 '사용'될 때 skill-builder까지 발동하는 패턴. "분석해줘"=사용(무관), "수정해줘"=수정(발동). 스킬 사용 ≠ 스킬 수정.
- **SKILL.md 2개 함정:** 세션에 이전 작업 폴더(skill-builder-v2/ 등)가 남은 채 zip하면 SKILL.md가 2개 들어가 설치 실패. zip 전 `find skill-name/ -name "SKILL.md" | wc -l`로 반드시 1개 확인.
- (초기 — 실수 발견 시 이 섹션에 직접 추가)
