# bash + python3 in-place 편집 템플릿 (v1.6 N3·N4)

## 왜 이게 필요한가

Cowork mode에서 `mnt/.claude/skills/...`는:
- Cowork Edit/Write tool이 **못 닿음** (connected folder 밖)
- DC edit_block도 **못 닿음** (VM 격리·호스트 fs 분리)
- 원본은 `read-only` (`-r--------`)

→ 유일한 작동 경로 = 세션 복사 + bash python3 in-place replace.

## 단일 스킬 편집 (1턴)

```bash
# 1) 세션 복사 + 권한
cp -r /sessions/{id}/mnt/.claude/skills/{skill}/ /sessions/{id}/{skill}/
chmod -R u+w /sessions/{id}/{skill}/

# 2) 편집 (heredoc 외부 PYEOF 토큰 충돌 주의 — INNER 권장)
cd /sessions/{id}/{skill} && python3 - << 'INNER'
p = "SKILL.md"
s = open(p, encoding="utf-8").read()

# 슬롯 (old, new) 쌍을 명시
edits = [
    ("old string A", "new string A"),
    ("old string B", "new string B"),
]
for o, n in edits:
    assert o in s, f"missing: {o[:50]}"
    s = s.replace(o, n, 1)

open(p, "w", encoding="utf-8").write(s)
print("OK", len(s), "bytes,", len(edits), "edits")
INNER

# 3) 검증
python3 /sessions/{id}/mnt/.claude/skills/skill-builder/scripts/validate.py /sessions/{id}/{skill}/

# 4) 패키징
cd /sessions/{id} && rm -f {skill}.skill && \
  zip -r {skill}.skill {skill}/ -x "*.pyc" "__pycache__/*" ".DS_Store" "evals/*"
```

## N개 스킬 batch 편집 (1턴)

```bash
# 1) 세션 복사 N개 (병렬)
for sk in A B C; do
  cp -r /sessions/{id}/mnt/.claude/skills/$sk/ /sessions/{id}/$sk/ &
done
wait
chmod -R u+w /sessions/{id}/{A,B,C}/

# 2) 단일 python3 1회 dict 처리
cd /sessions/{id} && python3 - << 'INNER'
edits = {
    "A": [("oldA1", "newA1"), ("oldA2", "newA2")],
    "B": [("oldB1", "newB1")],
    "C": [("oldC1", "newC1"), ("oldC2", "newC2"), ("oldC3", "newC3")],
}
for skill, pairs in edits.items():
    p = f"{skill}/SKILL.md"
    s = open(p, encoding="utf-8").read()
    for o, n in pairs:
        assert o in s, f"{skill}: missing {o[:40]}"
        s = s.replace(o, n, 1)
    open(p, "w", encoding="utf-8").write(s)
    print(f"{skill}: {len(pairs)} edits, {len(s)} bytes")
INNER

# 3) zip N개 병렬
for sk in A B C; do
  (cd /sessions/{id} && rm -f $sk.skill && zip -r $sk.skill $sk/ -x "*.pyc" "__pycache__/*" ".DS_Store" "evals/*") &
done
wait
```

## 핵심 룰

| 룰 | 이유 |
|---|---|
| `assert o in s` 필수 | replace 실패 시 silent fail 방지 |
| `replace(o, n, 1)` 1회만 | 중복 매칭 방지 |
| heredoc 토큰 = `INNER` | 외부 `PYEOF`와 충돌 방지 |
| 인코딩 명시 = `utf-8` | 한글 깨짐 방지 |
| dict 1회 통합 | 4번 갈아타기 → 0번 |
| zip 병렬 + wait | N배 가속 |

## Gotchas

| 함정 | 대응 |
|------|------|
| heredoc 안에서 `PYEOF` 사용 | bash 호출이 `PYEOF`를 외부 종료자로 인식 → SyntaxError. INNER로 |
| python heredoc 토큰 들여쓰기 | `<< 'INNER'`는 들여쓰기 안 됨. 라인 시작 위치 |
| replace 1번 vs all | 1번이 안전. 다중 매칭 시 의도치 않은 치환 |
| `assert` 없이 silent | 누락 발견 못 함. assert 필수 |
| 1줄짜리 sed 유혹 | 다중 라인·특수문자 시 깨짐. python3 유지 |
