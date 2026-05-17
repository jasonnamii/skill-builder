# 9-rules-template.md — skill-builder 베놈 골격 스니펫

신규 스킬 생성·기존 스킬 베놈 보강 시 SKILL.md에 강제 삽입할 7섹션 골격.

## frontmatter metadata 표준화

```yaml
metadata:
  author: jason
  version: "1.0.0"
```

## 본문 7섹션 골격

### 1. Skill Boundaries
```markdown
## Skill Boundaries

- **하는 것** — [핵심 작업 1~3개]
- **안 하는 것** — [경계 1](→ skill-X) · [경계 2](→ skill-Y)
```

### 2. When to Use
```markdown
## When to Use

- 사용자가 "[트리거 동사구]" — [상황]
- [상황 시나리오 2~5개]
- **안 쓸 때** — [부정 케이스 1~2개]
```

### 3. Prerequisites
```markdown
## Prerequisites

| # | 체크 | 미충족 시 |
|---|------|-----------|
| 1 | [의존 파일·상태] | [폴백·STOP·질문] |
```

### 4. Output Path
```markdown
## Output Path

| 산출물 | 경로 |
|---|---|
| [산출물명] | `mnt/outputs/...` 또는 `{VAULT}/...` |
```

### 5. Reference Index
```markdown
## Reference Index

| 파일 | 내용 | 언제 |
|---|---|---|
| `references/...` | [내용] | [읽는 시점] |
```

### 6. Next Phase
```markdown
## Next Phase

- [후속 작업] → `[skill-name]`
```

### 7. Failure Modes (Gotchas)
```markdown
## Failure Modes (Gotchas)

| 함정 | 대응 |
|---|---|
| [흔히 망치는 패턴] | [대응 1줄] |
```

## description 첫문장 평문화 (선택룰 8)

```
[권장] description: 외부 LLM도 이해 가능한 평문 한 문장. (이어서) P1: ... P2: ... NOT: ...
[비권장] description: 5층×6도메인×3모드 엔진. P1: ...  (압축어만)
```

## 9룰 grep 검증 (단일 heredoc 안)

```python
required = ["Skill Boundaries", "When to Use", "Prerequisites", "Output Path",
            "Reference Index", "Next Phase", "Failure Modes"]
missing = [r for r in required if r not in s]
assert not missing, f"9룰 누락: {missing}"
```
