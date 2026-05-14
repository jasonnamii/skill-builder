# Edit Protocol (v3.0)

본 문서는 SKILL.md의 ② 묶음 편집·검증 상세를 다룹니다. SKILL.md 본문은 핵심만 박제하고, 응용 패턴은 여기에 있습니다.

## 묶음 heredoc 표준 패턴

```bash
cd /sessions/$SESSION_ID && python3 << 'EOF'
import re
p = "skill-name/SKILL.md"
s = open(p).read()

# A. 편집
edits = [("OLD 1", "NEW 1"), ("OLD 2", "NEW 2")]
for o, n in edits:
    assert o in s, f"missing: {o[:40]}"
    s = s.replace(o, n, 1)
open(p, "w").write(s)

# B. 동일 heredoc 안 검증
m = re.search(r"^description: (.+)$", s, re.MULTILINE)
desc_len = len(m.group(1)) if m else 0
assert desc_len <= 1024, f"description {desc_len}/1024 초과"

lines = s.count(chr(10))
assert lines <= 500, f"SKILL.md {lines}줄 > 500"

# C. 동기 검증 (옵션) — description ↔ 본문 키워드 정합
if "P1" in m.group(1):
    p1_keywords = re.findall(r"P1[^.]+", m.group(1))
    # 본문에도 키워드 일부 존재해야 함

print(f"OK edits={len(edits)} desc={desc_len} lines={lines}")
EOF
```

**원칙:**
1. 편집·assert·len()·라인수 측정을 **단일 heredoc**에 묶는다
2. 외부 `head·tail·grep·wc -l` 재확인 ✗
3. 검증 실패 = AssertionError로 즉시 멈춤
4. 성공 = `print()` 한 줄로 종합 보고

## 전면 재작성 패턴

```bash
cd /sessions/$SESSION_ID && python3 << 'EOF'
import re
new = """---
name: skill-name
description: ...
---

# skill-name v3

본문...
"""
open("skill-name/SKILL.md", "w").write(new)
m = re.search(r"^description: (.+)$", new, re.MULTILINE)
assert len(m.group(1)) <= 1024
assert new.count(chr(10)) <= 500
print(f"written: {new.count(chr(10))} lines")
EOF
```

## 배치 (N개 동시)

```bash
cd /sessions/$SESSION_ID && python3 << 'EOF'
edits = {
    "skill-A": [("o1","n1"), ("o2","n2")],
    "skill-B": [("oX","nY")],
}
for skill, pairs in edits.items():
    p = f"{skill}/SKILL.md"
    s = open(p).read()
    for o, n in pairs:
        assert o in s, f"{skill}: missing {o[:40]}"
        s = s.replace(o, n, 1)
    open(p, "w").write(s)
print(f"OK {len(edits)} skills")
EOF
```

## 안티패턴

❌ **편집 후 매번 head·grep·ls로 확인:**
```bash
python3 -c "..." # 편집
head -30 SKILL.md    # 확인 1
grep "v3" SKILL.md   # 확인 2
ls references/       # 확인 3
wc -l SKILL.md       # 확인 4
```
→ 1턴 편집 + 4턴 확인 = 5턴. v2.0 시간 도둑의 정체.

✅ **묶음 heredoc 안 assert + print:**
```bash
python3 << 'EOF'
# 편집 + assert + print 1회
EOF
```
→ 1턴.
