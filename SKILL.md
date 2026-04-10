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
| 1 | **병렬 최대화** — 의존관계 없는 스킬은 **최대 4개 동시** 처리. 읽기·편집 각각을 병렬 tool call로 발행. 경미수정은 배치 모드로 1턴 일괄 |
| 2 | **수정 완료 = .skill 패키징 제공** — 패키징 없이 "수정했습니다"는 미완료 |
| 3 | **도구 우선순위: FS MCP > Cowork 빌트인** — FS `read_file`·`write_file`·`edit_file` 우선 사용. read-first 제약 없고 세션복사 불필요. FS 미응답 시에만 Cowork Read→Edit 폴백. `/tmp/` 사용 금지 |
| 4 | **게이트키퍼** — 스킬 SKILL.md를 수정·제작할 때 **반드시 skill-builder를 먼저 발동**. skill-builder 미발동 상태에서 스킬 파일 수정 착수 = FAIL. 단, 다른 스킬이 대화에서 단순 '사용/발동'되는 것에는 관여하지 않음 — 오직 스킬 파일 편집·제작 시에만 |

---

## 속도 원칙 (모든 경로에 적용)

| 원칙 | 구현 |
|------|------|
| **FS 직접 R/W** | FS `read_file`로 원본 읽기 → FS `write_file`로 수정본 직접 쓰기. **세션복사(cp) 제거** — 2단계를 1단계로 병합. 이유: Cowork Edit은 read-first 강제로 +1턴, cp는 +1턴 |
| **병렬 읽기** | N개 SKILL.md를 1턴에 N개 FS `read_file` 동시 발행 |
| **병렬 편집** | 서로 다른 파일을 1턴에 최대 6개 동시 (FS `write_file` 또는 `edit_file`) |
| **병렬 패키징** | N개 zip을 `&`+`wait`로 동시 |
| **단계 합치기** | 편집+description 검사를 동일 턴에 처리 |
| **조건부 스킵** | description 미변경 시 동기 검사 스킵 |

---

## 4경로 분기

| 경로 | 조건 | 실행 단계 | 스킵 |
|------|------|----------|------|
| **경미수정 FAST** | 지시 1-3줄, 섹션 구조 동일, description 변경 불필요 | FS read→FS write→패키징+제공 **(2턴)** | description 검사, 검증, 테스트 |
| **경미수정** | 지시 1-3줄, 섹션 구조 동일, description 변경 필요 | FS read→FS write(+description)→패키징+제공 **(2턴)** | 검증, 테스트 |
| **중간수정** | 섹션 신설·삭제·재배치, 레퍼런스 추가, 로직 변경 | FS read→FS write(+description)→검증→패키징+제공 **(3턴)** | 테스트 |
| **신규생성** | 스킬을 처음부터 만듦 | 설계(의도→트리거→작성)→검증→패키징+제공 | 테스트 (사용자 명시 시만) |

**판정:** 수정 개소 3 이하 + 섹션 동일 = 경미. 그 외 = 중간. 새 스킬 = 신규.

---

## 허브스포크 판정 (신규·수정 공통)

모든 경로에서 스킬 구조를 결정하거나 변경할 때 적용. **허브스포크가 맞으면 반드시 허브스포크로 만든다.**

### 판정 기준

| 조건 (하나라도 해당) | → 허브스포크 |
|---------------------|-------------|
| SKILL.md 단일 작성 시 >5KB 예상 | ✓ |
| 독립 참조 블록(경로별 절차, 스키마, 가이드 등) 2개+ | ✓ |
| 수정 중 발견: 단일인데 과밀(10KB 근접 또는 섹션 6개+) | ✓ 전환 |
| 해당 없음 — SKILL.md ≤5KB, 참조 블록 1개 이하 | 단일 유지 |

### 허브 작성 규칙

| 항목 | 규칙 |
|------|------|
| 허브 역할 | 분기 로직·절대 규칙·경로 판정만. **세부 절차는 포인터로 대체** |
| 허브 크기 | 목표 3KB, 최대 5KB |
| 포인터 문법 | `→ references/{파일명}.md 참조` (Read로 로딩 유도) |
| Gotchas | 허브에 유지 (즉시 참조 필요) |

### 스포크 분리 기준

| 스포크 대상 | 이유 |
|------------|------|
| 경로별 상세 절차 (코드·표·체크리스트) | 해당 경로 진입 시에만 필요 |
| 스키마·레퍼런스 (10KB+) | 참조 시에만 로딩 |
| 도메인 지식 (패턴 DB, 원리 목록 등) | 전체 로딩 불필요 |

**토큰 효과:** 허브만 즉시 로딩 → 필요 스포크만 Read → 불필요 토큰 60-70% 절감.

### 수정 중 전환 절차

기존 단일 스킬을 수정하다가 허브스포크가 맞다고 판단되면:

1. 분리 대상 섹션 식별 → `references/{이름}.md`로 이동
2. 원본 위치에 포인터 삽입: `→ references/{이름}.md 참조`
3. 허브 크기 ≤5KB 확인
4. 스포크 파일 누락·참조 깨짐 검증

---

## 배치 모드 (N개 스킬 동시 처리)

같은 유형의 단계를 모아서 병렬 발행: `FS read(A)+FS read(B)` → `FS write(A)+FS write(B)` → `zip A & zip B & wait` → 링크.
2개+ 스킬이 같은 경로일 때 적용. 경로가 다르면 같은 경로끼리 묶어 배치.

---

## 수정 경로 (경미 + 중간 공통)

### 1. FS read → 2. FS write (세션복사 제거)

```
# 1. 읽기: FS read_file로 원본 직접 읽기 (N개 동시 발행 가능)
#    경로: mnt/.claude/skills/{skill}/SKILL.md
#
# 2. 쓰기: FS write_file로 세션 디렉토리에 수정본 직접 쓰기
#    경로: ./{skill}/SKILL.md
#    ※ 세션복사(cp -r) 불필요 — write_file이 파일+디렉토리 생성
#    ※ 부분수정: FS edit_file 사용 가능 (read-first 제약 없음)
#    ※ write_file 사용 시 전체 내용 포함 확인 — 부분 누락 방지
```

### 3. description 동기 — 본문 수정이 description 범위에 영향 있으면 같은 턴에 갱신, 없으면 스킵.

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

### 5. 패키징 + 제공

```bash
zip -r {skill}.skill {skill}/ -x "*.pyc" -x "__pycache__/*" -x ".DS_Store" -x ".git/*" -x "*-workspace/*" -x "evals/*"
unzip -l {skill}.skill | head -5 && cp {skill}.skill mnt/outputs/
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

**허브스포크 판정:** 위 「허브스포크 판정」 섹션 기준으로 판정 → 해당 시 허브+스포크 구조로 작성. 허브(분기·규칙·포인터)는 ≤5KB, 세부내용은 `references/`로 분리.

**작성 규칙:** "왜" 설명 필수(이유 없는 지시→무시), 예시 1개+(없으면 출력 자의적), Gotchas 섹션 필수, ALWAYS/NEVER 남발 대신 이유 설명.

작성 완료 → 검증 체크리스트(위) → 패키징+제공(위).

---

## Gotchas

- **FS write_file 누락:** 전체 파일을 쓰므로 내용 일부 누락 주의. 수정 전 원본을 반드시 FS read로 확보한 뒤 수정본 전체를 write
- **Cowork Edit 폴백:** FS MCP 미응답 시에만 사용. Cowork Edit은 반드시 Read 선행 필요 — 이 제약이 +1턴 병목의 원인
- **볼트 직접배포:** mnt/.claude/skills/는 읽기전용. .skill 패키지→재설치만 반영됨
- **`/tmp/` 경로:** `/tmp/` 사용 금지. 세션 디렉토리만 사용
- **description↔본문 불일치:** description이 발동 판단 유일 입력. 본문 수정 시 반드시 동기 확인
- **zip만:** .skill은 zip. `tar -czf` 사용 시 설치 실패
- **순차 처리:** 독립 스킬은 반드시 병렬 tool call. 순차→턴 N배 낭비
- **오발동:** 스킬 '사용'≠스킬 '수정'. "분석해줘"=무관, "수정해줘"=발동
- **SKILL.md 2개:** zip 전 `find skill-name/ -name "SKILL.md" | wc -l`로 1개 확인
