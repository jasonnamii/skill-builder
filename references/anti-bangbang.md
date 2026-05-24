# 안티-뱅뱅 RCA 정본 (v3.2)

skill-builder 작업 중 발생한 반복 호출(뱅뱅이) 4대 원인 + 차단 패턴.

## A. 묶음 heredoc 실패 시 진단 콜 폭증

**증상:** heredoc 안 N개 edit 중 1개 실패. "어디까지 들어갔지?" 확인하려 sed·grep·cat 3~5회.

**원인:** assert 메시지 짧음 + heredoc 끝에 "적용 vs 스킵" 출력 없음.

**차단:**
```python
edits=[("A_old","A_new"),...]; applied,skipped=[],[]
for o,n in edits:
    if o in s: s=s.replace(o,n,1); applied.append(o[:30])
    else:
        import sys; sys.stderr.write(f"FAILED at: {o[:80]}\n")
        skipped.append(o[:60]); raise AssertionError(f"edit not applied: {o[:60]}")
open(p,"w").write(s)
print(f"applied={applied} skipped={skipped} len={len(s)}")
```

## B. VM ↔ Host 경로 혼동

VM bash와 host bash(DC)는 다른 파일시스템. 매핑:

| 경로 | VM bash | host bash(DC) |
|---|---|---|
| `/sessions/{id}/...` | ✅ | ❌ |
| `/Users/jason/...` | ❌ | ✅ |
| `mnt/outputs/` ↔ `~/Library/.../local_*/outputs/` | 양쪽 동일 | 양쪽 동일 |
| `mnt/.claude/skills/{X}/` | RO | ❌ |
| `~/github-repos/.../scripts/` | ❌ | ✅ |

**VM→Host 전달:** VM `cp .../patched mnt/outputs/` → DC `cp "$OUTPUTS/patched" ~/github-repos/...`

DC outputs 절대경로:
```bash
OUT=$(ls -td "$HOME/Library/Application Support/Claude/local-agent-mode-sessions"/*/*/local_*/outputs | head -1)
```

## C. 성능 패치 dry-run 통과 vs 실측 0초 컷

short-circuit(sha256·cache) 있는 스크립트는 동일 입력 시 본류 우회.

**절차:** ① 대상 grep `sha256\|cache\|skip` ② 발견 시 `rm .cache/...` ③ 실측

## D. sync 스크립트 환경 의존

`sync-to-host-plugin.sh`는 host shell 전용·git-sync env 의존. VM에서 호출 ✗.

**원칙:** skill-builder ④ = outputs 출고만 강제. host sync는 git-sync 스킬에 위임.

## 진단 출력 표준

모든 heredoc 마지막 줄 강제:
```python
print(f"applied={applied} skipped={skipped} len={len(s)}")
```
